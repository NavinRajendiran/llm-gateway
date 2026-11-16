from typing import Optional, List, Dict
from .config import PROVIDERS, get_active_providers
from .quota import quota
import tiktoken


def estimate_tokens(messages: List[Dict], model: str = "gpt-4") -> int:
    try:
        encoding = tiktoken.encoding_for_model("gpt-4")
        text = " ".join(
            [m.get("content", "") for m in messages if isinstance(m.get("content"), str)]
        )
        return len(encoding.encode(text)) + 80
    except Exception:
        text = " ".join([str(m.get("content", "")) for m in messages])
        return max(120, len(text) // 3)


def select_provider(
    requested_model: str, estimated_tokens: int = 500
) -> Optional[str]:
    """
    Select the best available provider based on:
    1. Whether the provider is configured (has key if required)
    2. Model support
    3. Remaining quota
    4. Priority score
    """
    candidates = []
    active = get_active_providers()

    for pid in active:
        config = PROVIDERS[pid]

        # Model matching
        model_ok = False
        generic_models = {
            "auto", "free", "gpt-4o-mini", "gpt-3.5-turbo",
            "gpt-4o", "gpt-4", "gpt-4-turbo"
        }
        if requested_model.lower() in generic_models:
            model_ok = True
        else:
            for m in config["models"]:
                if (
                    requested_model.lower() in m.lower()
                    or m.lower() in requested_model.lower()
                ):
                    model_ok = True
                    break

        if not model_ok:
            continue

        if not quota.is_available(pid, config["rpm"], config["tpd"], estimated_tokens):
            continue

        remaining = quota.get_remaining(pid, config["rpm"], config["tpd"])
        score = (
            config["priority"] * 100
            + (remaining["tokens"] / max(config["tpd"], 1)) * 40
            + remaining["rpm"] * 3
        )
        candidates.append((score, pid))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]


def map_model(requested_model: str, provider_id: str) -> str:
    """Map generic / requested model names to a concrete model on the provider."""
    config = PROVIDERS[provider_id]
    models = config["models"]

    generic = {
        "auto", "free", "gpt-4o-mini", "gpt-3.5-turbo",
        "gpt-4o", "gpt-4", "gpt-4-turbo"
    }
    if requested_model.lower() in generic:
        return models[0]

    # Try exact / partial match
    for m in models:
        if requested_model.lower() == m.lower():
            return m
    for m in models:
        if requested_model.lower() in m.lower() or m.lower() in requested_model.lower():
            return m

    return models[0]
