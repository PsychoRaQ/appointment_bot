# аиограм
from aiogram import Bot
# консьюмер
from src.nats.delayed_message_consumer import DelayedMessageConsumer
from src.nats.dispatch_consumer import DispatchConsumer
# натс
from nats.aio.client import Client
from nats.js.client import JetStreamContext
# логирование
import logging

logger = logging.getLogger(__name__)

'''
запуск консьюмеров
'''


# запуск консьюмера для отложенных уведомлений
async def start_delayed_consumer(
        nc: Client,
        js: JetStreamContext,
        bot: Bot,
        subject: str,
        stream: str,
        durable_name: str,
) -> None:
    consumer = DelayedMessageConsumer(
        nc=nc,
        js=js,
        bot=bot,
        subject=subject,
        stream=stream,
        durable_name=durable_name,
    )
    logger.info('Start delayed message consumer')
    await consumer.start()


# запуск консьюмера для рассылки
async def start_dispatch_consumer(
        nc: Client,
        js: JetStreamContext,
        bot: Bot,
        subject: str,
        stream: str,
        durable_name: str,
) -> None:
    consumer = DispatchConsumer(
        nc=nc,
        js=js,
        bot=bot,
        subject=subject,
        stream=stream,
        durable_name=durable_name,
    )
    logger.info('Start dispatch consumer')
    await consumer.start()
