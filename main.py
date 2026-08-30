import os
import logging
import asyncio

from dotenv import load_dotenv
from utils.file_utils import load_channels
from utils.datetime_utils import get_zrr_current_weekday
from client import LolkaClient
from bot import vs
from utils.logging_utils import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.environ["TOKEN"]

async def main():
    logger.info("====================")
    logger.info("Application started")

    logger.info("Loading channels")
    channels = load_channels()
    logger.info("Loaded %d channels", len(channels))

    weekday = get_zrr_current_weekday()
    logger.info("Current ZRR weekday: %d", weekday)

    client = LolkaClient(token=TOKEN)

    logger.info("Connecting client")
    async with client.connected():
        logger.info("Client connected")

        for channel in channels:
            channel_id = channel["id"]
            channel_type = channel["type"]
            logger.info("Processing channel: id=%s type=%s", channel_id, channel_type)

            if channel_type == "vs":
                await vs(
                    client=client,
                    channel_id=channel_id,
                    weekday=weekday,
                )

            logger.info("Finished processing channel: id=%s", channel_id)

    logger.info("Application finished")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logger.exception("Application crashed")
        raise