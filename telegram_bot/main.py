from __future__ import annotations

import os

from dotenv import load_dotenv
from telegram.ext import Application

from .app import build_application, configure_logging
from .config import load_config
from .watcher import start_watching


def main() -> None:
    configure_logging()

    # Allows local dev with a .env file, while still working in prod via env vars.
    load_dotenv()

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    assert token, "Missing TELEGRAM_BOT_TOKEN (set it in your env or in a .env file)"

    config = load_config()

    async def post_init(application: Application) -> None:
        application.bot_data["config"] = config

        if config.startup_chat_id is not None:
            start_watching(
                application,
                chat_id=config.startup_chat_id,
                room_id=config.bilibili_room_id,
                interval_offline_seconds=config.check_interval_offline_seconds,
                interval_online_seconds=config.check_interval_online_seconds,
            )

    application = build_application(token, post_init=post_init)
    application.run_polling()


if __name__ == "__main__":
    main()
