# 🎬 The Show Runner

AI-powered show production system for creating video content with custom characters.

## Features

- **📸 Characters** - Manage talent roster with reference images and voice settings
- **💡 Shows** - Create show concepts with episode planning
- **🎥 Production** - Generate scripts, audio, and video automatically
- **📤 Outputs** - Export for Spreaker (podcast), YouTube, TikTok/Instagram

## Tech Stack

- **Script Generation** - Claude 3.5 Sonnet
- **Voice Synthesis** - Hume AI (custom voices)
- **Video Generation** - LTX Video
- **Transcription** - OpenAI Whisper

## Quick Start

### Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your fork
4. Add API keys in Settings > Secrets

## API Keys Required

Add to `.streamlit/secrets.toml` (local) or Streamlit Cloud Secrets:

```toml
[api_keys]
anthropic = "sk-ant-..."
hume = "..."
ltx = "ltxv_..."
openai = "sk-..."
```

## Pre-loaded Content

- **AI House Cast** - Claire, VV, Olly, Pennie, Roxie with Hume voice IDs
- **Show Templates** - Sitcom, News Desk, Explainer, Talk Show

---

Built by [Inception Point AI](https://inceptionpoint.ai) ⚡
