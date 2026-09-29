import asyncio
import logging
from contextlib import asynccontextmanager, suppress

import lolka

logger = logging.getLogger(__name__)


class LolkaClient(lolka.Client):
    def __init__(self, token: str):
        super().__init__(intents=lolka.Intents.default())
        self._token = token

    async def on_ready(self):
        logger.info("Connected as %s (%s)", self.user, self.user.id)

    async def get_channel_history(
        self,
        channel_id: int,
        limit: int | None = 100,
    ) -> list[lolka.Message]:
        """Сообщения канала, от новых к старым."""
        channel = await self.fetch_channel(channel_id)
        messages = [
            message
            async for message in channel.history(limit=limit, oldest_first=False)
        ]
        logger.info("Channel history loaded: channel_id=%s messages=%d", channel_id, len(messages))
        return messages

    async def send_message(self, channel_id: int, content: str) -> lolka.Message:
        channel = await self.fetch_channel(channel_id)
        message = await channel.send(content)
        logger.info("Message sent: channel_id=%s message_id=%s length=%d", channel_id, message.id, len(content))
        return message

    async def delete_message(self, message: lolka.Message) -> None:
        await message.delete()
        logger.info("Message deleted: message_id=%s", message.id)

    @asynccontextmanager
    async def connected(self):
        """Запускает клиент, ждёт готовности и корректно закрывает его на выходе."""
        async with self:
            client_task = asyncio.create_task(self.start(self._token))
            ready_task = asyncio.create_task(self.wait_until_ready())

            done, _ = await asyncio.wait(
                {client_task, ready_task},
                return_when=asyncio.FIRST_COMPLETED,
            )

            if client_task in done:
                # start() завершился раньше, чем клиент стал ready:
                # поднимаем настоящее исключение, если оно есть.
                ready_task.cancel()
                with suppress(asyncio.CancelledError):
                    await ready_task
                await client_task
                raise RuntimeError("Client stopped before becoming ready")

            logger.info("Client is ready")
            try:
                yield self
            finally:
                logger.info("Closing client")
                await self.close()
                with suppress(asyncio.CancelledError):
                    await client_task
                logger.info("Client closed")
