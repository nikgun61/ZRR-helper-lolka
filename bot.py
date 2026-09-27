import logging

from client import LolkaClient
from utils.file_utils import find_file_by_prefix_and_read

logger = logging.getLogger(__name__)


async def vs(
        client: LolkaClient,
        channel_id: int,
        weekday: int
):
    logger.info("VS processing started: channel_id=%s weekday=%d", channel_id, weekday)
    await _delete_yesterday_content(
        client=client,
        channel_id=channel_id,
        yesterday_content=yesterday_content
    )

    await _publish_content(
        client=client,
        channel_id=channel_id,
        today_content=today_content
    )

    logger.info("VS processing finished: channel_id=%s", channel_id)


async def _delete_yesterday_content(
        client: LolkaClient,
        channel_id: int,
        yesterday_content: str
):
    logger.info("Loading messages to find yesterday content: channel_id=%s", channel_id)
    messages = await client.get_channel_history(channel_id=channel_id)
    logger.info("Loaded %d messages: channel_id=%s", len(messages), channel_id)

    for message in messages:
        if message.content == yesterday_content:
            logger.info("Yesterday message found: channel_id=%s message_id=%s", channel_id, message.id)
            await client.delete_message_object(message)
            logger.info("Yesterday message deleted: channel_id=%s message_id=%s", channel_id, message.id)
            return

    logger.info("Yesterday message not found: channel_id=%s", channel_id)


async def _publish_content(
        client: LolkaClient,
        channel_id: int,
        today_content: str
):
    logger.info("Loading latest message: channel_id=%s", channel_id)
    messages = await client.get_channel_history(
        channel_id=channel_id,
        limit=1
    )
    logger.info("Loaded %d latest messages: channel_id=%s", len(messages), channel_id)

    if messages and messages[0].content == today_content:
        logger.info("Today's message already published: channel_id=%s message_id=%s", channel_id, messages[0].id)
        return

    logger.info("Publishing today's message: channel_id=%s", channel_id)
    message = await client.send_message(
        channel_id=channel_id,
        content=today_content
    )
    logger.info("Today's message published: channel_id=%s message_id=%s", channel_id, message.id)


