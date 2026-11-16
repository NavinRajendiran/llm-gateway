from datetime import datetime
from typing import Dict
import threading


class QuotaTracker:
    def __init__(self):
        self._lock = threading.Lock()
        self._usage: Dict[str, Dict] = {}

    def _get_key(self, provider: str) -> str:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return f"{provider}:{today}"

    def record_usage(self, provider: str, tokens: int = 0, requests: int = 1):
        with self._lock:
            key = self._get_key(provider)
            if key not in self._usage:
                self._usage[key] = {"tokens": 0, "requests": 0, "last_request": None}

            self._usage[key]["tokens"] += tokens
            self._usage[key]["requests"] += requests
            self._usage[key]["last_request"] = datetime.utcnow()

    def get_remaining(self, provider: str, rpm_limit: int, tpd_limit: int) -> Dict:
        with self._lock:
            key = self._get_key(provider)
            usage = self._usage.get(key, {"tokens": 0, "requests": 0})

            remaining_tokens = max(0, tpd_limit - usage["tokens"])
            # Simple approximation for free tier
            remaining_rpm = max(0, rpm_limit - (usage["requests"] // 50))

            return {
                "tokens": remaining_tokens,
                "rpm": remaining_rpm,
                "used_tokens": usage["tokens"],
                "used_requests": usage["requests"],
            }

    def is_available(
        self, provider: str, rpm_limit: int, tpd_limit: int, estimated_tokens: int = 500
    ) -> bool:
        remaining = self.get_remaining(provider, rpm_limit, tpd_limit)
        return remaining["tokens"] >= estimated_tokens and remaining["rpm"] > 0


quota = QuotaTracker()
