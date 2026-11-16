import httpx
from typing import AsyncGenerator, Dict, Any
from .config import settings, PROVIDERS


async def call_provider(
    provider_id: str, payload: Dict[str, Any], stream: bool = False
) -> httpx.Response | AsyncGenerator:

    config = PROVIDERS[provider_id]
    api_key = getattr(settings, config["api_key_env"], "") or ""

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Free-LLM-Gateway/1.1",
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # Extra headers (e.g. OpenRouter)
    extra = config.get("extra_headers", {})
    headers.update(extra)

    # Build base URL (special handling for Cloudflare)
    base_url = config["base_url"]
    if provider_id == "cloudflare":
        account_id = getattr(settings, "CLOUDFLARE_ACCOUNT_ID", "") or ""
        base_url = base_url.replace("{account_id}", account_id)

    url = f"{base_url.rstrip('/')}/chat/completions"
    timeout = httpx.Timeout(180.0, connect=20.0)

    if stream:
        client = httpx.AsyncClient(timeout=timeout)
        req = client.build_request("POST", url, json=payload, headers=headers)
        response = await client.send(req, stream=True)
        return response
    else:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            return response
