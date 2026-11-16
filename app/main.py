from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import time

from .config import settings, PROVIDERS, get_active_providers
from .router import select_provider, map_model, estimate_tokens
from .providers import call_provider
from .quota import quota

app = FastAPI(
    title="Free LLM Gateway",
    description="Automatic free-tier LLM provider switcher covering all major free providers (OpenAI compatible)",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(authorization: Optional[str] = Header(None)):
    if not settings.GATEWAY_API_KEY:
        return
    if not authorization:
        raise HTTPException(401, "Missing Authorization header")
    token = authorization.replace("Bearer ", "").strip()
    if token != settings.GATEWAY_API_KEY:
        raise HTTPException(401, "Invalid API key")


@app.get("/")
async def root():
    active = get_active_providers()
    return {
        "message": "Free LLM Gateway is running",
        "version": "1.1.0",
        "active_providers": len(active),
        "providers": active,
        "docs": "/docs",
        "health": "/health",
        "models": "/v1/models",
        "stats": "/stats",
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": time.time(),
        "active_providers": len(get_active_providers()),
    }


@app.get("/v1/models")
async def list_models(authorization: Optional[str] = Header(None)):
    verify_api_key(authorization)

    models = []
    active = get_active_providers()

    for pid in active:
        config = PROVIDERS[pid]
        for m in config["models"]:
            models.append(
                {
                    "id": m,
                    "object": "model",
                    "created": 1677610602,
                    "owned_by": config["name"],
                    "provider": pid,
                }
            )

    # Generic aliases always available
    models.insert(
        0,
        {
            "id": "auto",
            "object": "model",
            "created": 1677610602,
            "owned_by": "free-llm-gateway",
            "provider": "auto",
        },
    )
    models.insert(
        1,
        {
            "id": "free",
            "object": "model",
            "created": 1677610602,
            "owned_by": "free-llm-gateway",
            "provider": "auto",
        },
    )

    return {"object": "list", "data": models}


@app.post("/v1/chat/completions")
async def chat_completions(
    request: Request, authorization: Optional[str] = Header(None)
):
    verify_api_key(authorization)

    body = await request.json()

    messages = body.get("messages", [])
    requested_model = body.get("model", "auto")
    stream = body.get("stream", False)
    max_tokens = body.get("max_tokens", 1024)

    if not messages:
        raise HTTPException(400, "messages is required")

    estimated = estimate_tokens(messages)

    last_error = None
    tried = set()

    # Try up to 4 different providers
    for attempt in range(4):
        provider_id = select_provider(requested_model, estimated)

        if not provider_id or provider_id in tried:
            if provider_id:
                quota.record_usage(provider_id, tokens=estimated * 3, requests=10)
            provider_id = select_provider(requested_model, estimated)

        if not provider_id:
            break

        tried.add(provider_id)
        actual_model = map_model(requested_model, provider_id)

        payload = {
            "model": actual_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": stream,
            "temperature": body.get("temperature", 0.7),
        }
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            if stream:
                response = await call_provider(provider_id, payload, stream=True)

                if response.status_code >= 400:
                    error_text = await response.aread()
                    raise Exception(f"{response.status_code}: {error_text.decode()[:300]}")

                async def event_generator():
                    try:
                        async for chunk in response.aiter_bytes():
                            yield chunk
                    finally:
                        await response.aclose()
                        quota.record_usage(
                            provider_id, tokens=estimated + max_tokens // 2
                        )

                return StreamingResponse(
                    event_generator(), media_type="text/event-stream"
                )

            else:
                response = await call_provider(provider_id, payload, stream=False)

                if response.status_code >= 400:
                    raise Exception(f"{response.status_code}: {response.text[:400]}")

                data = response.json()

                usage = data.get("usage", {})
                total_tokens = usage.get("total_tokens", estimated + max_tokens // 2)
                quota.record_usage(provider_id, tokens=total_tokens)

                data["_gateway"] = {
                    "provider": provider_id,
                    "provider_name": PROVIDERS[provider_id]["name"],
                    "model_used": actual_model,
                    "requested_model": requested_model,
                    "attempt": attempt + 1,
                }

                return JSONResponse(content=data)

        except Exception as e:
            last_error = str(e)
            quota.record_usage(provider_id, tokens=estimated * 2, requests=8)
            continue

    raise HTTPException(
        503,
        detail={
            "error": "All free providers are currently unavailable or rate-limited",
            "last_error": last_error,
            "tried_providers": list(tried),
            "active_providers": get_active_providers(),
        },
    )


@app.get("/stats")
async def stats(authorization: Optional[str] = Header(None)):
    verify_api_key(authorization)

    result = {}
    for pid in get_active_providers():
        config = PROVIDERS[pid]
        remaining = quota.get_remaining(pid, config["rpm"], config["tpd"])
        result[pid] = {
            "name": config["name"],
            "priority": config["priority"],
            "remaining_tokens_today": remaining["tokens"],
            "used_tokens_today": remaining["used_tokens"],
            "used_requests_today": remaining["used_requests"],
            "rpm_limit": config["rpm"],
            "tpd_limit": config["tpd"],
        }
    return {
        "active_providers": len(result),
        "providers": result,
    }
