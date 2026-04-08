# syntax=docker/dockerfile:1

FROM python:3.11-slim

# Install uv by copying the official binary (fast + reproducible)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_DEV=1

WORKDIR /app

# Copy project and install deps from the lockfile
COPY . /app
RUN uv sync --locked

# This bot uses Telegram long-polling (no inbound HTTP server), so no ports are exposed.
CMD ["uv", "run", "python", "-m", "telegram_bot"]
