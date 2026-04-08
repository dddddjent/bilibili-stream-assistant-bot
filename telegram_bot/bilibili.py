from __future__ import annotations

from typing import Any

import httpx

_BILIBILI_ROOM_INFO_URL = "https://api.live.bilibili.com/room/v1/Room/get_info"

_HEADERS = {
    # Without a UA/Referer, Bilibili may respond with HTTP 412.
    "User-Agent": "curl/8.5.0",
    "Referer": "https://live.bilibili.com/",
    "Accept": "application/json",
}


async def fetch_live_status(room_id: int) -> int:
    """Return live_status (1=live, 0=offline) for the given Bilibili room_id."""

    async with httpx.AsyncClient(timeout=10.0, headers=_HEADERS, follow_redirects=True) as client:
        response = await client.get(_BILIBILI_ROOM_INFO_URL, params={"room_id": room_id})
        response.raise_for_status()
        payload: dict[str, Any] = response.json()

    assert payload.get("code") == 0, payload

    data = payload["data"]
    assert isinstance(data, dict)

    live_status = data["live_status"]
    assert isinstance(live_status, int)

    return live_status
