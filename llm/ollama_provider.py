import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Optional

from llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama adapter with hardware-friendly, model-aware settings.

    The application stays model-agnostic: change MODEL_NAME and the provider
    automatically adjusts context/output limits and keeps a loaded model warm
    for a short period. A long request timeout prevents slow cold starts on
    low-RAM machines from being mistaken for connection failures.
    """

    def __init__(self, model_name: Optional[str] = None, base_url: Optional[str] = None):
        self.model_name = model_name or os.getenv("MODEL_NAME", "llama3.1:8b")
        self.base_url = (
            base_url
            or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        ).rstrip("/")

        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "900"))
        self.keep_alive = os.getenv("OLLAMA_KEEP_ALIVE", "5m")
        self.max_retries = int(os.getenv("OLLAMA_RETRIES", "1"))
        self.temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.15"))

        # Smaller models need less context/output on constrained machines.
        # Larger models get more room when the user switches models.
        self.options = self._model_options(self.model_name)

        # Bypass Windows/system proxy settings for local Ollama.
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({})
        )

    @staticmethod
    def _model_options(model_name: str) -> dict:
        name = model_name.lower()
        match = re.search(r"(?<!\d)(\d+(?:\.\d+)?)b(?:\b|[-_:])", name)
        size_b = float(match.group(1)) if match else 8.0

        if size_b <= 2:
            return {"temperature": 0.15, "num_predict": 1100, "num_ctx": 4096}
        if size_b <= 4:
            return {"temperature": 0.15, "num_predict": 1400, "num_ctx": 6144}
        return {"temperature": 0.15, "num_predict": 1800, "num_ctx": 8192}

    def _post_generate(self, prompt: str) -> dict:
        payload = json.dumps({
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "keep_alive": self.keep_alive,
            "options": self.options,
        }).encode("utf-8")

        url = f"{self.base_url}/api/generate"
        request = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.opener.open(request, timeout=self.timeout) as response:
            response_data = response.read().decode("utf-8")

        try:
            data = json.loads(response_data)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Ollama returned invalid response: {response_data[:500]}"
            ) from e

        raw = data.get("response", "")
        if not raw:
            raise RuntimeError(f"Ollama returned no generated response: {data}")

        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Ollama returned malformed JSON:\n{raw[:1200]}"
            ) from e

    def generate_json(self, prompt: str) -> dict:
        url = f"{self.base_url}/api/generate"
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return self._post_generate(prompt)
            except (urllib.error.URLError, TimeoutError, OSError, RuntimeError) as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(1.5)
                    continue

        raise RuntimeError(
            f"Could not complete Ollama generation at {url}. "
            f"Model: {self.model_name}. Timeout: {self.timeout:.0f}s. "
            f"The model may be cold-starting or the machine may be under memory pressure. "
            f"Original error: {last_error}"
        ) from last_error
