"""Обработчики каналов."""

import logging
from dataclasses import dataclass

from client import LolkaClient
from config import VS_DIR
from utils.datetime_utils import get_previous_weekday
from utils.file_utils import find_file_by_prefix_and_read

logger = logging.getLogger(__name__)

# Сколько последних сообщений канала просматривать.
HISTORY_LIMIT = 100


@dataclass(frozen=True)
class VsContent:
    weekday: int
    today: str
    yesterday: str


def _normalize(text: str) -> str:
    # Платформа может обрезать пробелы/переводы строк по краям,
    # а у файла обычно есть завершающий \n — сравниваем без них.
    return text.strip()


def _load_day(weekday: int) -> str:
    content = _normalize(find_file_by_prefix_and_read(VS_DIR, f"{weekday}_"))
    if not content:
        raise ValueError(f"Файл контента для дня {weekday} в {VS_DIR} пуст")
    return content


def load_vs_content(weekday: int) -> VsContent:
    yesterday_weekday = get_previous_weekday(weekday)
    content = VsContent(
        weekday=weekday,
        today=_load_day(weekday),
        yesterday=_load_day(yesterday_weekday),
    )
    logger.info(
        "VS content loaded: today=%d (length=%d) yesterday=%d (length=%d)",
        weekday, len(content.today), yesterday_weekday, len(content.yesterday),
    )
    return content


async def process_vs_channel(client: LolkaClient, channel_id: int, content: VsContent) -> None:
    logger.info("VS processing started: channel_id=%s weekday=%d", channel_id, content.weekday)

    history = await client.get_channel_history(channel_id, limit=HISTORY_LIMIT)
    own_messages = [m for m in history if m.author.id == client.user.id]

    if content.yesterday == content.today:
        logger.info("Yesterday and today content are identical, nothing to delete: channel_id=%s", channel_id)
    else:
        yesterday_message = next(
            (m for m in own_messages if _normalize(m.content) == content.yesterday),
            None,
        )
        if yesterday_message is None:
            logger.info("Yesterday message not found: channel_id=%s", channel_id)
        else:
            logger.info("Deleting yesterday message: channel_id=%s message_id=%s", channel_id, yesterday_message.id)
            await client.delete_message(yesterday_message)

    today_message = next(
        (m for m in own_messages if _normalize(m.content) == content.today),
        None,
    )
    if today_message is not None:
        logger.info("Today's message already published: channel_id=%s message_id=%s", channel_id, today_message.id)
    else:
        await client.send_message(channel_id, content.today)

    logger.info("VS processing finished: channel_id=%s", channel_id)
