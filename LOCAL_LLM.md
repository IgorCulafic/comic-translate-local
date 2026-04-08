# Local LLM Support

This fork of [comic-translate](https://github.com/ogkalu2/comic-translate) adds support for
locally-hosted LLMs as a translation backend, with no API key or subscription required.

## What was added

### `modules/translation/llm/local_llm.py`
A full translation engine that connects to any OpenAI-compatible local inference server.
Supports text-only and multimodal (vision) models.

Compatible backends:
- **KoboldCpp** (default port 5001)
- **Ollama** (default port 11434)
- **LM Studio** (default port 1234)
- **llama.cpp server**
- **text-generation-webui** with OpenAI extension
- **Jan**, **LocalAI**, and any other OpenAI-compatible server

### `modules/translation/factory.py`
Wired `LocalLLMTranslation` into the translation factory alongside GPT, Claude, Gemini,
and Deepseek. Local LLM is explicitly excluded from the subscription/token check so it
works without any account.

### `app/ui/settings/credentials_page.py`
Added a full settings UI panel for Local LLM configuration:
- Server URL field (defaults to `http://localhost:11434`)
- Model name field (e.g. `llama3`, `mistral`, `gemma2`)
- Optional API key field (most local servers accept anything or none)
- Vision/image input toggle for multimodal models

## Setup

1. Start your local inference server (Ollama, KoboldCpp, etc.)
2. Launch comic-translate: `uv run comic.py`
3. Go to Settings > Credentials
4. Find the **Local LLM** section
5. Enter your server URL and model name
6. In the main window, select **Local LLM** as the translator

## Notes

- A 300 second timeout is set by default since local models can be slow, especially on CPU
- Vision input works if your model supports it and you enable the toggle in credentials
- Tested with Llama 3 8B via KoboldCpp and Ollama

## Original Project

All credit for the core comic translation pipeline goes to
[ogkalu2](https://github.com/ogkalu2) and contributors.
See the original [README](README.md) for full documentation.
