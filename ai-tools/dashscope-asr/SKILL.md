---
name: dashscope-asr
description: >
 Transcribe audio files and voice messages to text using DashScope Paraformer-v2 async ASR API.
 Activate when: user sends a voice note, audio file, or voice message; user asks to transcribe,
 convert speech-to-text, or recognize audio content; user says "听写", "转录", "语音转文字",
 "转文字", or any audio file (ogg, wav, mp3, m4a) is attached. Requires DASHSCOPE_API_KEY.
---

# DashScope ASR — Audio Transcription

## Prerequisites

- `requests` Python package installed (`pip install requests`)
- `DASHSCOPE_API_KEY` env var set

## Workflow

1. Audio file/voice note arrives → run:
 ```bash
 python scripts/transcribe.py <audio_file_path>

Use the file path from the inbound attachment.

2. Script output is the transcribed text — reply to user with it.

Supported: .ogg .wav .mp3 .m4a

API

The script submits an async task to DashScope Paraformer-v2, polls until done (≤60s), returns text.

Troubleshooting

• 401 Unauthorized: check DASHSCOPE_API_KEY is valid DashScope key (not Telegram bot token)
• File not found: verify the path from attachment metadata
• Timeout: audio too long or API overloaded; retry manually
