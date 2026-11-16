from pydantic_settings import BaseSettings
from typing import Dict, Any, List


class Settings(BaseSettings):
    # Gateway authentication (clients use this as OPENAI_API_KEY)
    GATEWAY_API_KEY: str = "sk-free-llm-gateway"

    # ========== Provider API Keys ==========
    # Leave empty if you don't have the key — that provider will be skipped
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    AION_API_KEY: str = ""
    ZAI_API_KEY: str = ""              # Zhipu AI / BigModel
    COHERE_API_KEY: str = ""
    CLOUDFLARE_API_TOKEN: str = ""
    CLOUDFLARE_ACCOUNT_ID: str = ""
    SILICONFLOW_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""           # NVIDIA NIM
    MODELSCOPE_API_KEY: str = ""
    GONKA_API_KEY: str = ""
    LLM7_TOKEN: str = ""               # optional free token
    KILO_API_KEY: str = ""             # usually not needed for free pool
    OVH_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()


# ============================================================
# All practical free providers from awesome-free-llm-apis
# Only providers with OpenAI-compatible endpoints are included
# ============================================================

PROVIDERS: Dict[str, Dict[str, Any]] = {

    # ---------- Highest priority / fastest ----------
    "groq": {
        "name": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "models": [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.2-90b-vision-preview",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        "priority": 100,
        "rpm": 30,
        "tpd": 200_000,
        "supports_streaming": True,
        "requires_key": True,
    },

    "gemini": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "models": [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemma-3-27b-it",
            "gemma-3-12b-it",
        ],
        "priority": 95,
        "rpm": 15,
        "tpd": 1_000_000,
        "supports_streaming": True,
        "requires_key": True,
    },

    # ---------- Strong free pools ----------
    "openrouter": {
        "name": "OpenRouter Free",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "models": [
            "openrouter/free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "google/gemma-3-27b-it:free",
            "google/gemma-2-9b-it:free",
            "qwen/qwen-2.5-72b-instruct:free",
            "qwen/qwen-2.5-7b-instruct:free",
            "mistralai/mistral-small-3.1-24b-instruct:free",
            "mistralai/mistral-7b-instruct:free",
            "microsoft/phi-3-mini-128k-instruct:free",
            "huggingface/zephyr-7b-beta:free",
            "openchat/openchat-7b:free",
        ],
        "priority": 90,
        "rpm": 20,
        "tpd": 200_000,
        "supports_streaming": True,
        "requires_key": True,
        "extra_headers": {
            "HTTP-Referer": "https://free-llm-gateway.onrender.com",
            "X-Title": "Free LLM Gateway",
        },
    },

    "kilo": {
        "name": "Kilo Code",
        "base_url": "https://api.kilo.ai/api/gateway",
        "api_key_env": "KILO_API_KEY",
        "models": [
            "kilo-auto/free",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "nvidia/nemotron-3.5-lightning:free",
            "nvidia/nemotron-3.5-super-vl:free",
            "cohere/north-mini-code:free",
            "openrouter/free",
            "dots-studio/dots-3-note-preview:free",
        ],
        "priority": 85,
        "rpm": 200,
        "tpd": 500_000,
        "supports_streaming": True,
        "requires_key": False,
    },

    "llm7": {
        "name": "LLM7.io",
        "base_url": "https://api.llm7.io/v1",
        "api_key_env": "LLM7_TOKEN",
        "models": [
            "gpt-oss:20b",
            "mistral-nemo-instruct-2407",
            "codestral-latest",
            "deepseek-coder",
        ],
        "priority": 80,
        "rpm": 60,
        "tpd": 150_000,
        "supports_streaming": True,
        "requires_key": False,
    },

    # ---------- Solid free tiers ----------
    "siliconflow": {
        "name": "SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "api_key_env": "SILICONFLOW_API_KEY",
        "models": [
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "deepseek-ai/DeepSeek-V2.5",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "google/gemma-2-27b-it",
            "Pro/Qwen/Qwen2.5-72B-Instruct",
        ],
        "priority": 75,
        "rpm": 100,
        "tpd": 500_000,
        "supports_streaming": True,
        "requires_key": True,
    },

    "nvidia": {
        "name": "NVIDIA NIM",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key_env": "NVIDIA_API_KEY",
        "models": [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "nvidia/llama-3.3-nemotron-super-49b-v1",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "meta/llama-3.3-70b-instruct",
            "meta/llama-3.1-405b-instruct",
            "meta/llama-3.1-70b-instruct",
            "meta/llama-3.1-8b-instruct",
            "google/gemma-2-27b-it",
            "google/gemma-2-9b-it",
            "mistralai/mistral-large-2-instruct",
            "mistralai/mixtral-8x22b-instruct-v0.1",
            "microsoft/phi-3.5-moe-instruct",
        ],
        "priority": 70,
        "rpm": 40,
        "tpd": 300_000,
        "supports_streaming": True,
        "requires_key": True,
    },

    "cloudflare": {
        "name": "Cloudflare Workers AI",
        "base_url": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1",
        "api_key_env": "CLOUDFLARE_API_TOKEN",
        "extra_env": ["CLOUDFLARE_ACCOUNT_ID"],
        "models": [
            "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
            "@cf/meta/llama-3.1-8b-instruct",
            "@cf/meta/llama-3.2-3b-instruct",
            "@cf/meta/llama-4-scout-17b-16e-instruct",
            "@cf/qwen/qwen1.5-14b-chat-awq",
            "@cf/google/gemma-2-9b-it",
            "@cf/mistral/mistral-7b-instruct-v0.2",
            "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
            "@cf/openai/gpt-oss-120b",
        ],
        "priority": 65,
        "rpm": 50,
        "tpd": 100_000,
        "supports_streaming": True,
        "requires_key": True,
    },

    # ---------- Provider APIs ----------
    "aion": {
        "name": "Aion Labs",
        "base_url": "https://api.aionlabs.ai/v1",
        "api_key_env": "AION_API_KEY",
        "models": [
            "aion-labs/aion-3.0",
            "aion-labs/aion-3.0-mini",
            "aion-labs/aion-2.0",
            "aion-labs/aion-rp-llama-3.1-8b",
        ],
        "priority": 60,
        "rpm": 15,
        "tpd": 20_000,
        "supports_streaming": True,
        "requires_key": True,
    },

    "zai": {
        "name": "Z AI (Zhipu)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_env": "ZAI_API_KEY",
        "models": [
            "glm-4.7-flash",
            "glm-4.5-flash",
            "glm-4.6v-flash",
            "glm-4-flash",
            "glm-4-flashx",
            "glm-4-air",
            "glm-4-airx",
            "glm-4-long",
        ],
        "priority": 55,
        "rpm": 30,
        "tpd": 100_000,
        "supports_streaming": True,
        "requires_key": True,
    },

    "cohere": {
        "name": "Cohere",
        "base_url": "https://api.cohere.ai/compatibility/v1",
        "api_key_env": "COHERE_API_KEY",
        "models": [
            "command-a-03-2025",
            "command-r-plus-08-2024",
            "command-r-08-2024",
            "command-r7b-12-2024",
            "command-a-reasoning-08-2025",
            "command-light",
            "command-light-nightly",
        ],
        "priority": 50,
        "rpm": 20,
        "tpd": 50_000,
        "supports_streaming": True,
        "requires_key": True,
        "notes": "Non-commercial use only on free tier",
    },

    # ---------- Other free / generous tiers ----------
    "modelscope": {
        "name": "ModelScope",
        "base_url": "https://api-inference.modelscope.cn/v1",
        "api_key_env": "MODELSCOPE_API_KEY",
        "models": [
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-32B-Instruct",
            "Qwen/Qwen2.5-14B-Instruct",
            "Qwen/Qwen2.5-7B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "deepseek-ai/DeepSeek-V2.5",
            "Shanghai_AI_Laboratory/internlm2_5-20b-chat",
        ],
        "priority": 45,
        "rpm": 20,
        "tpd": 100_000,
        "supports_streaming": True,
        "requires_key": True,
    },

    "gonka": {
        "name": "Gonka Broker",
        "base_url": "https://proxy.gonkabroker.com/v1",
        "api_key_env": "GONKA_API_KEY",
        "models": [
            "MiniMaxAI/MiniMax-M2.7",
            "deepseek-ai/DeepSeek-V4-Flash-0731",
            "zai-org/GLM-5.3-Flash",
        ],
        "priority": 40,
        "rpm": 10,
        "tpd": 50_000,
        "supports_streaming": True,
        "requires_key": True,
    },

    "ovh": {
        "name": "OVHcloud AI Endpoints",
        "base_url": "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
        "api_key_env": "OVH_API_KEY",
        "models": [
            "Meta-Llama-3_3-70B-Instruct",
            "Meta-Llama-3_1-70B-Instruct",
            "Meta-Llama-3_1-8B-Instruct",
            "Mistral-Nemo-Instruct-2407",
            "Mixtral-8x7B-Instruct-v0.1",
            "Qwen2.5-72B-Instruct",
            "DeepSeek-R1-Distill-Llama-70B",
        ],
        "priority": 35,
        "rpm": 2,
        "tpd": 20_000,
        "supports_streaming": True,
        "requires_key": False,
    },
}


def get_active_providers() -> List[str]:
    """Return list of provider IDs that have the required keys configured."""
    active = []
    for pid, config in PROVIDERS.items():
        requires_key = config.get("requires_key", True)
        api_key = getattr(settings, config["api_key_env"], "") or ""

        if requires_key and not api_key:
            continue

        # Special case for Cloudflare (needs account id too)
        if pid == "cloudflare":
            account_id = getattr(settings, "CLOUDFLARE_ACCOUNT_ID", "") or ""
            if not account_id:
                continue

        active.append(pid)
    return active
