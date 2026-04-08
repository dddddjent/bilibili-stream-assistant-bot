from __future__ import annotations

import logging

from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters

from .handlers import echo, help_cmd, start


def configure_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
    )


def build_application(token: str) -> Application:
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, echo))

    return application
