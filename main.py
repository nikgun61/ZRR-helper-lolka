import asyncio
import logging
import sys

from bot import load_vs_content, process_vs_channel
from client import LolkaClient
from config import CHANNELS_FILE, LOG_DIR, load_settings
from utils.datetime_utils import get_zrr_current_weekday
from utils.file_utils import load_channels
from utils.logging_utils import setup_logging

logger = logging.getLogger(__name__)

SUPPORTED_TYPES = {"vs"}


async def run() -> int:
    """Обрабатывает все каналы. Возвращает число каналов, завершившихся ошибкой."""
    settings = load_settings()

    channels = load_channels(CHANNELS_FILE)
    logger.info("Loaded %d channels", len(channels))

    unknown = sorted({c.type for c in channels} - SUPPORTED_TYPES)
    if unknown:
        raise ValueError(f"Неизвестные типы каналов в {CHANNELS_FILE.name}: {', '.join(unknown)}")

    weekday = get_zrr_current_weekday()
    logger.info("Current ZRR weekday: %d", weekday)

    # Контент грузим до подключения: если файла нет, падаем сразу,
    # не открывая соединение.
    vs_content = load_vs_content(weekday) if any(c.type == "vs" for c in channels) else None

    failed = 0
    client = LolkaClient(token=settings.token)
    async with client.connected():
        for channel in channels:
            logger.info("Processing channel: id=%s type=%s comment=%r", channel.id, channel.type, channel.comment)
            try:
                if channel.type == "vs":
                    await process_vs_channel(client, channel.id, vs_content)
            except Exception:
                failed += 1
                logger.exception("Channel processing failed: id=%s", channel.id)
    return failed


def main() -> int:
    setup_logging(LOG_DIR)
    logger.info("====================")
    logger.info("Application started")
    try:
        failed = asyncio.run(run())
    except Exception:
        logger.exception("Application crashed")
        return 1

    if failed:
        logger.error("Application finished with errors: failed_channels=%d", failed)
        return 1
    logger.info("Application finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())
