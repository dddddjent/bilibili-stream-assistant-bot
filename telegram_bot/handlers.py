from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from .bilibili import create_bilibili_client, fetch_room_info, fetch_streamer_name
from .config import Config
from .watcher import is_watching, start_watching, stop_watching


def _get_config(context: ContextTypes.DEFAULT_TYPE) -> Config:
    config_any = context.application.bot_data.get("config")
    assert isinstance(config_any, Config)
    return config_any


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start: check immediately, then poll with different intervals."""

    assert update.effective_chat is not None

    config = _get_config(context)

    started_rooms: list[int] = []
    already_running_rooms: list[int] = []

    for room_id in config.bilibili_room_ids:
        started = start_watching(
            context.application,
            chat_id=update.effective_chat.id,
            room_id=room_id,
            interval_offline_seconds=config.check_interval_offline_seconds,
            interval_online_seconds=config.check_interval_online_seconds,
            notify_online_only=config.notify_online_only,
        )
        (started_rooms if started else already_running_rooms).append(room_id)

    if started_rooms:
        suffix = "" if not already_running_rooms else f" ({len(already_running_rooms)} rooms were already running)"
        mode = "online-only" if config.notify_online_only else "all-status"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "Watching started. I will check immediately, then poll with: "
                f"offline={config.check_interval_offline_seconds:g}s, online={config.check_interval_online_seconds:g}s "
                f"for {len(started_rooms)} rooms. mode={mode}{suffix}"
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

    async with create_bilibili_client() as client:
        infos = await asyncio.gather(
            *(fetch_room_info(client, room_id=room_id) for room_id in config.bilibili_room_ids)
        )

        uids = [info.uid for info in infos]
        unique_uids = sorted(set(uids))
        names = await asyncio.gather(*(fetch_streamer_name(client, mid=uid) for uid in unique_uids))

    uid_to_name = dict(zip(unique_uids, names, strict=True))

    lines: list[str] = []
    for info in infos:
        name = uid_to_name.get(info.uid, f"mid={info.uid}")
        state = "STREAMING" if info.live_status == 1 else "OFFLINE"
        lines.append(f"{name}: live_status={info.live_status} ({state})")

    watching_text = "yes" if is_watching(context.application, update.effective_chat.id) else "no"
    lines.append(f"watching={watching_text}")

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="\n".join(lines),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help."""

    assert update.effective_chat is not None

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=(
            "Commands:\n"
            "- /start: start checking now (all configured rooms); offline/online use different intervals\n"
            "- /stop: stop sending\n"
            "- /status: check once (all configured rooms)\n"
        ),
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo plain text messages."""

    assert update.message is not None
    assert update.message.text is not None
    await update.message.reply_text(update.message.text)
