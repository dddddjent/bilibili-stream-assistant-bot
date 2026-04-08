from __future__ import annotations

import os

from dotenv import load_dotenv

from .app import build_application, configure_logging


def main() -> None:
    configure_logging()

    # Allows local dev with a .env file, while still working in prod via env vars.
    load_dotenv()

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    assert token, "Missing TELEGRAM_BOT_TOKEN (set it in your env or in a .env file)"

    application = build_application(token)
    application.run_polling()


if __name__ == "__main__":
    main()
