from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start."""

    assert update.message is not None
    await update.message.reply_text("Hi! Send me any text and I will echo it back.")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help."""

    assert update.message is not None
    await update.message.reply_text("Commands: /start, /help. Any other text is echoed.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo plain text messages."""

    assert update.message is not None
    assert update.message.text is not None
    await update.message.reply_text(update.message.text)
