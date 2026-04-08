from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Config:
    bilibili_room_id: int
    check_interval_offline_seconds: float
    check_interval_online_seconds: float
    startup_chat_id: int | None


def load_config() -> Config:
    room_id_raw = os.environ.get("BILIBILI_ROOM_ID", "1990572299")

    # Legacy: if you only set CHECK_INTERVAL_SECONDS, we use it for both states.
    interval_legacy_raw = os.environ.get("CHECK_INTERVAL_SECONDS", "20")
    interval_offline_raw = os.environ.get("CHECK_INTERVAL_OFFLINE_SECONDS", interval_legacy_raw)
    interval_online_raw = os.environ.get("CHECK_INTERVAL_ONLINE_SECONDS", interval_legacy_raw)

    startup_chat_id_raw = os.environ.get("TELEGRAM_CHAT_ID")

    room_id = int(room_id_raw)
    interval_offline = float(interval_offline_raw)
    interval_online = float(interval_online_raw)
    startup_chat_id = int(startup_chat_id_raw) if startup_chat_id_raw else None

    assert interval_offline > 0
    assert interval_online > 0

    return Config(
        bilibili_room_id=room_id,
        check_interval_offline_seconds=interval_offline,
        check_interval_online_seconds=interval_online,
        startup_chat_id=startup_chat_id,
    )
