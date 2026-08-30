import asyncio
import logging

from contextlib import asynccontextmanager
import lolka

logger = logging.getLogger(__name__)

class LolkaClient(lolka.Client):
    def __init__(self, token: str):
        super().__init__(
            intents=lolka.Intents.default()
        )
        self.token = token

    async def on_ready(self):
        logger.info("Connected as %s (%s)", self.user,self.user.id)

    async def get_channel_history(
        self,
        channel_id: int,
        limit: int | None = 100,
    ) -> list[lolka.Message]:
        logger.info("Fetching channel: channel_id=%s", channel_id)
        channel = await self.fetch_channel(channel_id)
        logger.info("Channel fetched: channel_id=%s", channel_id)

        logger.info("Loading channel history: channel_id=%s limit=%s", channel_id, limit)
        messages = [
            message
            async for message in channel.history(
                limit=limit,
                oldest_first=False,
            )
        ]
        logger.info("Channel history loaded: channel_id=%s messages=%d", channel_id, len(messages))

        return messages

    async def delete_message(
        self,
        channel_id: int,
        message_id: int,
    ) -> None:
        logger.info("Fetching channel for message deletion: channel_id=%s", channel_id)
        channel = await self.fetch_channel(channel_id)

        logger.info("Fetching message: channel_id=%s message_id=%s", channel_id, message_id)
        message = await channel.fetch_message(message_id)

        logger.info("Deleting message: message_id=%s", message_id)

        await message.delete()

        logger.info("Message deleted: message_id=%s",message_id)

    async def send_message(
            self,
            channel_id: int,
            content: str,
    ) -> lolka.Message:
        logger.info("Fetching channel for sending message: channel_id=%s", channel_id)
        channel = await self.fetch_channel(channel_id)

        logger.info("Sending message: channel_id=%s content_length=%d", channel_id, len(content))
        message = await channel.send(content)
        logger.info("Message sent: channel_id=%s message_id=%s", channel_id, message.id)

        return message

    async def delete_message_object(
        self,
        message: lolka.Message,
    ) -> None:
        logger.info("Deleting message object: message_id=%s", message.id)
        await message.delete()
        logger.info("Message object deleted: message_id=%s", message.id)

    @asynccontextmanager
    async def connected(self):
        logger.info("Starting client")
        async with self:
            client_task = asyncio.create_task(
                self.start(self.token)
            )
            logger.info("Client task created")

            ready_task = asyncio.create_task(
                self.wait_until_ready()
            )
            logger.info("Waiting for client readiness")

            done, _ = await asyncio.wait(
                {
                    client_task,
                    ready_task,
                },
                return_when=asyncio.FIRST_COMPLETED,
            )

            if client_task in done:
                # Если start() упал раньше, чем клиент стал ready,
                # здесь сразу получим настоящее исключение.
                await client_task
                raise RuntimeError("Client stopped before becoming ready")

            await ready_task
            logger.info("Client is ready")

            try:
                yield self
            finally:
                logger.info("Closing client")
                await self.close()

                logger.info("Waiting for client task to finish")
                await client_task
                logger.info("Client closed")