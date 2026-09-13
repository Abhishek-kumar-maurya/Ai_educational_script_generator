import json
import os
import urllib.request
from typing import Optional

from llm.base import LLMProvider
from core.profiles import model_profile


class OllamaProvider(LLMProvider):
    def __init__(self, model_name=None, base_url=None):
        self.model_name = model_name or os.getenv("MODEL_NAME", "llama3.1:8b")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).rstrip("/")
        self.profile = model_profile(self.model_name)

    def _request(self, prompt: str, num_predict: Optional[int] = None) -> str:
        options = {
            "temperature": self.profile["temperature"],
            "num_predict": num_predict or self.profile["num_predict"],
            "num_ctx": self.profile["num_ctx"],
        }
        payload = json.dumps({
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "keep_alive": "10m",
            "options": options,
        }).encode("utf-8")
        url = f"{self.base_url}/api/generate"
        request = urllib.request.Request(
            url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
        )
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(request, timeout=self.profile["timeout"]) as response:
                response_data = response.read().decode("utf-8")
        except Exception as e:
            raise RuntimeError(
                f"Could not generate with Ollama at {url}. The model may still be loading. "
                f"Please wait and retry. Original error: {e}"
            ) from e
        try:
            data = json.loads(response_data)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Ollama returned invalid API response: {response_data[:500]}") from e
        raw = data.get("response", "")
        if not raw:
            raise RuntimeError(f"Ollama returned no generated response: {data}")
        return raw

    def generate_json(self, prompt: str) -> dict:
        raw = self._request(prompt)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as first_error:
            # Small local models can truncate long JSON. Retry once with a much
            # stricter compact-output instruction instead of failing the whole app.
            retry_prompt = prompt + """

IMPORTANT RETRY: Your previous JSON was incomplete. Regenerate it from scratch.
Make the JSON compact: use 6-8 scenes, short visual descriptions, short OTS/SFX,
and concise narration. Keep all required concepts. Return the COMPLETE JSON object,
including the final closing brackets. Output JSON only.
"""
            raw2 = self._request(retry_prompt, num_predict=max(self.profile["num_predict"], 2200))
            try:
                return json.loads(raw2)
            except json.JSONDecodeError as second_error:
                raise RuntimeError(
                    "Ollama generated incomplete JSON twice. The model reached its output limit. "
                    "Try a shorter target duration or retry once the model is warm. "
                    f"Last output preview: {raw2[:1200]}"
                ) from second_error
