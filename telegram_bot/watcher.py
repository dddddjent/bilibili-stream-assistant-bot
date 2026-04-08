from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx
from telegram.ext import Application

from .bilibili import fetch_live_status

logger = logging.getLogger(__name__)

_WATCH_TASKS_KEY = "watch_tasks"


def _get_watch_tasks(application: Application) -> dict[int, asyncio.Task[None]]:
    tasks_any = application.bot_data.setdefault(_WATCH_TASKS_KEY, {})
    assert isinstance(tasks_any, dict)
    tasks: dict[int, asyncio.Task[None]] = tasks_any
    return tasks


def is_watching(application: Application, chat_id: int) -> bool:
    tasks = _get_watch_tasks(application)
    task = tasks.get(chat_id)
    return task is not None and not task.done()


def stop_watching(application: Application, chat_id: int) -> bool:
    tasks = _get_watch_tasks(application)
    task = tasks.pop(chat_id, None)
    if task is None:
        return False

    task.cancel()
    return True


def start_watching(
    application: Application,
    *,
    chat_id: int,
    room_id: int,
    interval_seconds: float,
) -> bool:
    tasks = _get_watch_tasks(application)
    existing = tasks.get(chat_id)
    if existing is not None and not existing.done():
        return False

    task = application.create_task(
        _watch_loop(
            application,
            chat_id=chat_id,
            room_id=room_id,
            interval_seconds=interval_seconds,
        )
    )
    tasks[chat_id] = task
    return True


async def _watch_loop(
    application: Application,
    *,
    chat_id: int,
    room_id: int,
    interval_seconds: float,
) -> None:
    while True:
        try:
            live_status = await fetch_live_status(room_id)
            state = "STREAMING" if live_status == 1 else "OFFLINE"
            await application.bot.send_message(
                chat_id=chat_id,
                text=f"Bilibili room {room_id}: live_status={live_status} ({state})",
            )
        except (httpx.HTTPError, AssertionError, KeyError, TypeError, ValueError) as exc:
            logger.exception("Live check failed")
            await application.bot.send_message(
                chat_id=chat_id,
                text=f"Bilibili room {room_id}: check failed: {exc}",
            )

        await asyncio.sleep(interval_seconds)
