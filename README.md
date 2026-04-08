# Comic Translate — Local LLM Fork

Fork of [ogkalu2/comic-translate](https://github.com/ogkalu2/comic-translate) adding support
for locally-hosted LLMs as a translation backend. Translate manga, manhwa, webtoons and comics
with no API key, no subscription, and no data leaving your machine.

---

## What this fork adds

The original project requires a GPT, Claude, or Gemini API subscription for translation.
This fork adds **Local LLM** as a first-class translation option alongside the existing cloud providers,
using any OpenAI-compatible local inference server.

### Compatible backends
- **KoboldCpp** — recommended, tested (default port 5001)
- **Ollama** (default port 11434)
- **LM Studio** (default port 1234)
- **llama.cpp server**
- **text-generation-webui** with OpenAI extension
- **Jan**, **LocalAI**, and any other OpenAI-compatible server

### Changes made
| File | Change |
|------|--------|
| `modules/translation/llm/local_llm.py` | New translation engine — full OpenAI-compatible API client with vision support |
| `modules/translation/factory.py` | Wired Local LLM into engine factory, excluded from subscription check |
| `app/ui/settings/credentials_page.py` | Settings UI: server URL, model name, API key, vision toggle |
| `app/ui/settings/settings_page.py` | Registered Local LLM in settings page |
| `app/ui/settings/settings_ui.py` | Added Local LLM to translator list |
| `modules/translation/processor.py` | Pipeline integration |
| `modules/utils/pipeline_config.py` | Config support |

---

## Example

<!-- Add your before/after translation screenshots here -->
<!-- Recommended: side by side original page and translated output -->
<!-- Format: ![Description](docs/images/example_before.jpg) -->

*Screenshots coming soon — run the app and translate a page to see results.*

---

## Setup

Same as the original project. Install Python 3.12 and uv, then:

```bash
git clone https://github.com/IgorCulafic/comic-translate-local
cd comic-translate-local
uv init --python 3.12
uv add -r requirements.txt --compile-bytecode
```

If you have an NVIDIA GPU:
```bash
uv pip install onnxruntime-gpu
```

Run:
```bash
uv run comic.py
```

---

## Using Local LLM

1. Start your local inference server (KoboldCpp, Ollama, etc.) and load a model
2. Go to **Settings → Credentials**
3. Find the **Local LLM** section
4. Fill in:
   - **Server URL** — e.g. `http://localhost:5001` for KoboldCpp, `http://localhost:11434` for Ollama
   - **Model** — model name/tag e.g. `llama3`, `mistral`, `gemma2`
   - **API Key** — leave blank for most local servers
   - **Vision toggle** — enable if your model supports image input
5. In the main window, select **Local LLM** as the translator
6. Load your comic and translate as normal

### Recommended models

Any instruction-tuned model works. Better multilingual models give better translation quality.

- **Llama 3 8B / 70B** — good general quality, strong English output
- **Mistral 7B** — fast, good for European language pairs
- **Qwen 2.5** — excellent for CJK (Chinese, Japanese, Korean) translation
- **Gemma 2 9B** — solid all-rounder

A 300 second timeout is set by default since local models can be slow on CPU.

---

## Original Project

All credit for the comic translation pipeline — text detection, OCR, inpainting, rendering —
goes to [ogkalu2](https://github.com/ogkalu2) and contributors.

See [LOCAL_LLM.md](LOCAL_LLM.md) for a focused summary of the changes in this fork.

Full original documentation: [README (original)](https://github.com/ogkalu2/comic-translate#readme)
