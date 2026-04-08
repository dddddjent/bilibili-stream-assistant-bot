# Telegram Bot (uv)

Minimal Telegram bot built with **python-telegram-bot** and managed via **uv**.

This bot checks a Bilibili live room every **20 seconds** (configurable) and sends the `live_status` to your Telegram chat.

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

## Usage

- Send `/start` to the bot in Telegram: it will begin sending a message every `CHECK_INTERVAL_SECONDS` with
  the Bilibili `live_status` (1=streaming, 0=offline).
- Send `/stop` to stop the repeating messages.
- Send `/status` to check once.

## Config

Set these in `.env`:

- `BILIBILI_ROOM_ID` (default: `1990572299`)
- `CHECK_INTERVAL_SECONDS` (default: `20`)

Optional:

- `TELEGRAM_CHAT_ID`: if set, the bot will start sending messages to that chat immediately on startup.
