# Telegram Bot (uv)

Minimal Telegram bot built with **python-telegram-bot** and managed via **uv**.

This bot checks one or more Bilibili live rooms and sends the `live_status` to your Telegram chat.
It uses **different polling intervals** depending on whether the stream is offline vs streaming.

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

- Send `/start` to the bot in Telegram: it will check immediately, then keep polling the Bilibili
  `live_status` (1=streaming, 0=offline) using different intervals depending on whether the stream is live.
- Send `/stop` to stop the repeating messages.
- Send `/status` to check once.

## Config

Set these in `.env`:

- `BILIBILI_ROOM_IDS` (default: `1990572299`) — comma/space-separated, e.g. `1990572299,12345678`
  - Note: `BILIBILI_ROOM_ID` is no longer used.
- `CHECK_INTERVAL_OFFLINE_SECONDS` (recommended e.g. `20`)
- `CHECK_INTERVAL_ONLINE_SECONDS` (recommended e.g. `60`)

Legacy:

- `CHECK_INTERVAL_SECONDS`: used for both online/offline if the two variables above are not set.

Optional:

- `TELEGRAM_CHAT_ID`: if set, the bot will start sending messages to that chat immediately on startup.
