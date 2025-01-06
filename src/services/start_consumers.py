# аиограм
from aiogram import Bot
# консьюмер
from src.nats.consumer import DelayedMessageConsumer
# натс
from nats.aio.client import Client
from nats.js.client import JetStreamContext
# логирование
import logging

logger = logging.getLogger(__name__)

'''
запуск консьюмера
'''


async def start_delayed_consumer(
        nc: Client,
        js: JetStreamContext,
        bot: Bot,
        subject: str,
        stream: str,
        durable_name: str,
        subject_2: str,
        stream_2: str,
) -> None:
    consumer = DelayedMessageConsumer(
        nc=nc,
        js=js,
        bot=bot,
        subject=subject,
        stream=stream,
        durable_name=durable_name,

        subject_2=subject_2,
        stream_2=stream_2,
    )
    logger.info('Start delayed message consumer')
    await consumer.start()
