from __future__ import annotations

from dataclasses import dataclass
import os
import re


@dataclass(frozen=True, slots=True)
class Config:
    bilibili_room_ids: tuple[int, ...]
    check_interval_offline_seconds: float
    check_interval_online_seconds: float
    startup_chat_id: int | None

    # If true, only send repeating messages while a room is streaming.
    # Offline rooms are still polled, but no "OFFLINE" messages are sent.
    notify_online_only: bool


def _parse_room_ids(raw: str) -> tuple[int, ...]:
    parts = [p for p in re.split(r"[\s,]+", raw.strip()) if p]
    room_ids = tuple(int(p) for p in parts)
    assert room_ids, "BILIBILI_ROOM_IDS must not be empty"
    assert all(rid > 0 for rid in room_ids)
    return room_ids


_TRUE_STRINGS = {"1", "true", "yes", "y", "on"}
_FALSE_STRINGS = {"0", "false", "no", "n", "off", ""}


def _parse_bool_env(raw: str | None, *, key: str) -> bool:
    if raw is None:
        return False

    value = raw.strip().lower()
    assert value in (_TRUE_STRINGS | _FALSE_STRINGS), (
        f"Invalid {key}={raw!r}. Expected one of: "
        f"{sorted(_TRUE_STRINGS | _FALSE_STRINGS)}"
    )
    return value in _TRUE_STRINGS


def load_config() -> Config:
    room_ids_raw = os.environ.get("BILIBILI_ROOM_IDS", "1990572299")

    # Legacy: if you only set CHECK_INTERVAL_SECONDS, we use it for both states.
    interval_legacy_raw = os.environ.get("CHECK_INTERVAL_SECONDS", "20")
    interval_offline_raw = os.environ.get("CHECK_INTERVAL_OFFLINE_SECONDS", interval_legacy_raw)
    interval_online_raw = os.environ.get("CHECK_INTERVAL_ONLINE_SECONDS", interval_legacy_raw)

    startup_chat_id_raw = os.environ.get("TELEGRAM_CHAT_ID")
    notify_online_only_raw = os.environ.get("NOTIFY_ONLINE_ONLY")

    room_ids = _parse_room_ids(room_ids_raw)
    interval_offline = float(interval_offline_raw)
    interval_online = float(interval_online_raw)
    startup_chat_id = int(startup_chat_id_raw) if startup_chat_id_raw else None
    notify_online_only = _parse_bool_env(notify_online_only_raw, key="NOTIFY_ONLINE_ONLY")

    assert interval_offline > 0
    assert interval_online > 0

    return Config(
        bilibili_room_ids=room_ids,
        check_interval_offline_seconds=interval_offline,
        check_interval_online_seconds=interval_online,
        startup_chat_id=startup_chat_id,
        notify_online_only=notify_online_only,
    )
