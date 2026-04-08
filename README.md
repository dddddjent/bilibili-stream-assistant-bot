# Telegram Bot (uv)

Minimal Telegram bot built with **python-telegram-bot** and managed via **uv**.

## Prerequisites

- Python 3.11+
- `uv` (https://github.com/astral-sh/uv)

## Setup

1) Create a bot token via **@BotFather** on Telegram.

2) Create your local env file:

```bash
cp .env.example .env
# edit .env and set TELEGRAM_BOT_TOKEN=...
```

3) Sync dependencies:

```bash
uv sync
```

## Run

Template command:

```bash
uv run python -m telegram_bot
```

What it does:

- `/start` and `/help` commands
- echoes any plain text message
