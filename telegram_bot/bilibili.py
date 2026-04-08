from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

_BILIBILI_ROOM_INFO_URL = "https://api.live.bilibili.com/room/v1/Room/get_info"
_BILIBILI_USER_CARD_URL = "https://api.bilibili.com/x/web-interface/card"

_HEADERS = {
    # Without a UA/Referer, Bilibili may respond with HTTP 412.
    "User-Agent": "curl/8.5.0",
    "Referer": "https://live.bilibili.com/",
    "Accept": "application/json",
}

_CARD_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.bilibili.com/",
    "Accept": "application/json",
}


def create_bilibili_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=10.0, headers=_HEADERS, follow_redirects=True)


@dataclass(frozen=True, slots=True)
class RoomInfo:
    uid: int
    live_status: int


async def fetch_room_info(client: httpx.AsyncClient, *, room_id: int) -> RoomInfo:
    response = await client.get(_BILIBILI_ROOM_INFO_URL, params={"room_id": room_id})
    response.raise_for_status()
    payload: dict[str, Any] = response.json()

    assert payload.get("code") == 0, payload

    data = payload["data"]
    assert isinstance(data, dict)

    uid = data["uid"]
    assert isinstance(uid, int)

    live_status = data["live_status"]
    assert isinstance(live_status, int)

    return RoomInfo(uid=uid, live_status=live_status)


async def fetch_streamer_name(client: httpx.AsyncClient, *, mid: int) -> str:
    response = await client.get(
        _BILIBILI_USER_CARD_URL,
        params={"mid": str(mid)},
        headers=_CARD_HEADERS,
    )
    response.raise_for_status()
    payload: dict[str, Any] = response.json()

    assert payload.get("code") == 0, payload

    data = payload["data"]
    assert isinstance(data, dict)

    card = data["card"]
    assert isinstance(card, dict)

    name = card["name"]
    assert isinstance(name, str)
    assert name

    return name
