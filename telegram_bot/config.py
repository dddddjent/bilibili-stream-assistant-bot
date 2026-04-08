from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Config:
    bilibili_room_id: int
    check_interval_seconds: float
    startup_chat_id: int | None


def load_config() -> Config:
    room_id_raw = os.environ.get("BILIBILI_ROOM_ID", "1990572299")
    interval_raw = os.environ.get("CHECK_INTERVAL_SECONDS", "20")
    startup_chat_id_raw = os.environ.get("TELEGRAM_CHAT_ID")

    room_id = int(room_id_raw)
    interval = float(interval_raw)
    startup_chat_id = int(startup_chat_id_raw) if startup_chat_id_raw else None

    assert interval > 0

    return Config(
        bilibili_room_id=room_id,
        check_interval_seconds=interval,
        startup_chat_id=startup_chat_id,
    )
