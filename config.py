"""Пути и настройки приложения."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Все пути строятся от корня проекта, а не от текущей директории,
# чтобы бот одинаково работал и из консоли, и из cron/systemd.
PROJECT_ROOT = Path(__file__).resolve().parent

CHANNELS_FILE = PROJECT_ROOT / "channels.json"
VS_DIR = PROJECT_ROOT / "vs"
LOG_DIR = PROJECT_ROOT / "logs"
ENV_FILE = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class Settings:
    token: str


def load_settings() -> Settings:
    load_dotenv(ENV_FILE)
    token = os.environ.get("TOKEN", "").strip()
    if not token:
        raise RuntimeError(f"Переменная TOKEN не задана (ожидается в окружении или в {ENV_FILE})")
    return Settings(token=token)
