from typing import Any
import numpy as np
import requests
import json

from .base import BaseLLMTranslation


class LocalLLMTranslation(BaseLLMTranslation):
    """
    Translation engine for locally-hosted LLMs using an OpenAI-compatible API.

    Supports any backend that exposes an OpenAI-compatible /v1/chat/completions
    endpoint, including:
      - KoboldCpp  (http://localhost:5001)
      - Ollama     (http://localhost:11434)
      - LM Studio  (http://localhost:1234)
      - llama.cpp server
      - text-generation-webui with OpenAI extension
      - Jan, LocalAI, etc.

    The user supplies:
      - api_url:  Base URL of the local server (e.g. "http://localhost:11434")
      - model:    Model name/tag (e.g. "llama3", "mistral", "gemma2")
      - api_key:  Optional — most local servers accept any string or none at all.
    """

    def __init__(self):
        super().__init__()
        self.model = None
        self.api_key = "local"          # Placeholder; most servers ignore this
        self.api_base_url = "http://localhost:11434"  # Sensible Ollama default
        self.supports_images = False    # Flip to True if model supports vision

    def initialize(
        self,
        settings: Any,
        source_lang: str,
        target_lang: str,
        tr_key: str,
        **kwargs,
    ) -> None:
        """
        Pull connection details from the "Local LLM" credentials section in settings.

        Args:
            settings:   Settings object (provides get_credentials / get_llm_settings).
            source_lang: Source language name.
            target_lang: Target language name.
            tr_key:     Translator key string (e.g. "Local LLM").
        """
        # Call the grandparent (BaseLLMTranslation) initialiser to set up
        # language pairs, temperature, top_p, max_tokens, etc.
        super().initialize(settings, source_lang, target_lang, **kwargs)

        # Longer timeout because local models can be slow on CPU
        self.timeout = 300

        credentials = settings.get_credentials(settings.ui.tr(tr_key))

        raw_url = credentials.get("api_url", "").rstrip("/")
        self.api_base_url = raw_url if raw_url else "http://localhost:11434"

        self.model = credentials.get("model", "").strip() or "llama3"

        api_key = credentials.get("api_key", "").strip()
        self.api_key = api_key if api_key else "local"

        # Read the vision toggle set by the user in the Advanced/Credentials settings
        self.supports_images = bool(credentials.get("supports_images", False))

    # ------------------------------------------------------------------
    # Core translation logic
    # ------------------------------------------------------------------

    def _perform_translation(
        self, user_prompt: str, system_prompt: str, image: np.ndarray
    ) -> str:
        """
        Call the local server's OpenAI-compatible chat completions endpoint.

        Most local backends (Ollama, KoboldCpp, LM Studio, llama.cpp) expose
        exactly the same JSON schema as the OpenAI API, so we can reuse the
        familiar message format.

        Image input is supported only when `self.supports_images` is True AND
        the user has enabled "Provide Image as Input to AI" in the LLMs settings
        panel.  Multimodal support depends entirely on the loaded model — if the
        model does not support vision the server will simply return an error.

        Args:
            user_prompt:   The assembled translation request text.
            system_prompt: Role/instruction text placed in the system turn.
            image:         Comic page as a numpy array (BGR, from OpenCV).

        Returns:
            Raw response string from the model (expected to be a JSON blob that
            `set_texts_from_json` can parse).
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Build the message list.  We always include both a system turn and a
        # user turn because that is the format every major local backend accepts.
        if self.supports_images and self.img_as_llm_input and image is not None:
            encoded_image, mime_type = self.encode_image(image)
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{encoded_image}"
                            },
                        },
                    ],
                },
            ]
        else:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            # stream=False is the default but being explicit prevents issues
            # with backends that require it to be stated.
            "stream": False,
        }

        endpoint = f"{self.api_base_url}/v1/chat/completions"

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(payload),
                timeout=self.timeout,
            )
            response.raise_for_status()
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Could not connect to local LLM server at '{self.api_base_url}'. "
                "Make sure the server is running and the URL is correct."
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"Request to local LLM server timed out after {self.timeout}s. "
                "The model may still be loading — try again, or increase the timeout."
            )
        except requests.exceptions.RequestException as exc:
            error_msg = f"Local LLM API request failed: {exc}"
            if hasattr(exc, "response") and exc.response is not None:
                try:
                    error_msg += f" — {json.dumps(exc.response.json())}"
                except Exception:
                    error_msg += f" — HTTP {exc.response.status_code}"
            raise RuntimeError(error_msg)
        except (KeyError, IndexError) as exc:
            raise RuntimeError(
                f"Unexpected response format from local LLM server: {exc}. "
                "The server may not be using an OpenAI-compatible API."
            )
