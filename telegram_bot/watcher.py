from __future__ import annotations

import asyncio
import logging

import httpx
from telegram.ext import Application

from .bilibili import create_bilibili_client, fetch_room_info, fetch_streamer_name

logger = logging.getLogger(__name__)

_WATCH_TASKS_KEY = "watch_tasks"
_STREAMER_NAME_CACHE_KEY = "streamer_name_cache"


def _get_watch_tasks(application: Application) -> dict[int, dict[int, asyncio.Task[None]]]:
    tasks_any = application.bot_data.setdefault(_WATCH_TASKS_KEY, {})
    assert isinstance(tasks_any, dict)
    tasks: dict[int, dict[int, asyncio.Task[None]]] = tasks_any
    return tasks


def _get_streamer_name_cache(application: Application) -> dict[int, str]:
    cache_any = application.bot_data.setdefault(_STREAMER_NAME_CACHE_KEY, {})
    assert isinstance(cache_any, dict)
    cache: dict[int, str] = cache_any
    return cache


async def _resolve_streamer_name(application: Application, *, client: httpx.AsyncClient, uid: int) -> str:
    cache = _get_streamer_name_cache(application)
    cached = cache.get(uid)
    if cached is not None:
        return cached

    name = await fetch_streamer_name(client, mid=uid)
    cache[uid] = name
    return name


def is_watching(application: Application, chat_id: int) -> bool:
    tasks = _get_watch_tasks(application)
    room_tasks = tasks.get(chat_id)
    if not room_tasks:
        return False
    return any(not task.done() for task in room_tasks.values())


def stop_watching(application: Application, chat_id: int) -> bool:
    tasks = _get_watch_tasks(application)
    room_tasks = tasks.pop(chat_id, None)
    if not room_tasks:
        return False

    for task in room_tasks.values():
        task.cancel()
    return True


def start_watching(
    application: Application,
    *,
    chat_id: int,
    room_id: int,
    interval_offline_seconds: float,
    interval_online_seconds: float,
    notify_online_only: bool,
) -> bool:
    tasks = _get_watch_tasks(application)
    room_tasks = tasks.setdefault(chat_id, {})

    existing = room_tasks.get(room_id)
    if existing is not None and not existing.done():
        return False

    task = application.create_task(
        _watch_loop(
            application,
            chat_id=chat_id,
            room_id=room_id,
            interval_offline_seconds=interval_offline_seconds,
            interval_online_seconds=interval_online_seconds,
            notify_online_only=notify_online_only,
        )
    )
    room_tasks[room_id] = task
    return True


async def _watch_loop(
    application: Application,
    *,
    chat_id: int,
    room_id: int,
    interval_offline_seconds: float,
    interval_online_seconds: float,
    notify_online_only: bool,
) -> None:
    last_live_status: int | None = None
    last_display_name = "Bilibili"

    async with create_bilibili_client() as client:
        while True:
            sleep_seconds = interval_offline_seconds

            try:
                room_info = await fetch_room_info(client, room_id=room_id)
                last_live_status = room_info.live_status

                sleep_seconds = (
                    interval_online_seconds if room_info.live_status == 1 else interval_offline_seconds
                )

                try:
                    display_name = await _resolve_streamer_name(
                        application,
                        client=client,
                        uid=room_info.uid,
                    )
                except (httpx.HTTPError, AssertionError, KeyError, TypeError, ValueError):
                    logger.exception("Streamer name lookup failed")
                    display_name = f"mid={room_info.uid}"

                last_display_name = display_name

                state = "STREAMING" if room_info.live_status == 1 else "OFFLINE"
                should_notify = (not notify_online_only) or (room_info.live_status == 1)
                if should_notify:
                    await application.bot.send_message(
                        chat_id=chat_id,
                        text=(
                            f"{display_name}: live_status={room_info.live_status} ({state}). "
                            f"next_check_in={sleep_seconds:g}s"
                        ),
                    )
            except (httpx.HTTPError, AssertionError, KeyError, TypeError, ValueError) as exc:
                logger.exception("Room check failed")

                if last_live_status is not None:
                    sleep_seconds = interval_online_seconds if last_live_status == 1 else interval_offline_seconds

                should_notify = (not notify_online_only) or (last_live_status == 1)
                if should_notify:
                    await application.bot.send_message(
                        chat_id=chat_id,
                        text=f"{last_display_name}: check failed: {exc}. next_check_in={sleep_seconds:g}s",
                    )

            await asyncio.sleep(sleep_seconds)
