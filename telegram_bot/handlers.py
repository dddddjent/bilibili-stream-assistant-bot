from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from .bilibili import fetch_live_status
from .config import Config
from .watcher import is_watching, start_watching, stop_watching


def _get_config(context: ContextTypes.DEFAULT_TYPE) -> Config:
    config_any = context.application.bot_data.get("config")
    assert isinstance(config_any, Config)
    return config_any


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start: start sending live_status every CHECK_INTERVAL_SECONDS."""

    assert update.effective_chat is not None

    config = _get_config(context)

    started = start_watching(
        context.application,
        chat_id=update.effective_chat.id,
        room_id=config.bilibili_room_id,
        interval_seconds=config.check_interval_seconds,
    )

    if started:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Watching started. I will message this chat every "
                f"{config.check_interval_seconds:g}s with live_status for room {config.bilibili_room_id}."
            ),
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Already watching this chat. Use /stop to stop.",
        )


async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stop: stop the repeating messages."""

    assert update.effective_chat is not None

    stopped = stop_watching(context.application, update.effective_chat.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Stopped." if stopped else "Nothing to stop.",
    )


async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status: check once and reply."""

    assert update.effective_chat is not None

    config = _get_config(context)

    live_status = await fetch_live_status(config.bilibili_room_id)
    state = "STREAMING" if live_status == 1 else "OFFLINE"

    watching_text = "yes" if is_watching(
        context.application, update.effective_chat.id) else "no"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            f"Room {config.bilibili_room_id}: live_status={live_status} ({state}). "
            f"watching={watching_text}"
        ),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help."""

    assert update.effective_chat is not None

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Commands:\n"
            "- /start: start sending live_status every 20s (or CHECK_INTERVAL_SECONDS)\n"
            "- /stop: stop sending\n"
            "- /status: check once\n"
        ),
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo plain text messages."""

    assert update.message is not None
    assert update.message.text is not None
    await update.message.reply_text(update.message.text)
