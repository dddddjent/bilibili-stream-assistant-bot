from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters

from .handlers import echo, help_cmd, start_cmd, status_cmd, stop_cmd


def configure_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
    )


def build_application(
    token: str,
    *,
    post_init: Callable[[Application], Awaitable[None]] | None = None,
) -> Application:
    builder = ApplicationBuilder().token(token)
    if post_init is not None:
        builder = builder.post_init(post_init)

    application = builder.build()

    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("stop", stop_cmd))
    application.add_handler(CommandHandler("status", status_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    return application
