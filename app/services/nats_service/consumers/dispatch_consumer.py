import logging
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js import JetStreamContext

logger = logging.getLogger(__name__)

'''
консьюмер рассылки
'''


class DispatchConsumer:
    def __init__(
            self,
            nc: Client,
            js: JetStreamContext,
            bot: Bot,
            subject: str,
            stream: str,
            durable_name: str,

    ) -> None:
        self.nc = nc
        self.js = js
        self.bot = bot
        self.subject = subject
        self.stream = stream
        self.durable_name = durable_name

    # подключение консьюмера
    async def start(self) -> None:
        self.stream_sub = await self.js.subscribe(
            subject=self.subject,
            stream=self.stream,
            cb=self.on_message,
            durable=self.durable_name,
            manual_ack=True,
        )

    # обработчик полученного сообщения
    async def on_message(self, msg: Msg):
        sent_time = datetime.fromtimestamp(float(msg.headers.get('Tg-Delayed-Msg-Timestamp')), tz=timezone.utc)
        delay = int(msg.headers.get('Tg-Delayed-Msg-Delay'))
        # Проверяем наступило ли время обработки сообщения
        if sent_time + timedelta(seconds=delay) > datetime.now().astimezone():
            # Если время обработки не наступило - вычисляем сколько секунд осталось до обработки
            new_delay = (sent_time + timedelta(seconds=delay) - datetime.now().astimezone()).total_seconds()
            # Отправляем nak с временем задержки
            await msg.nak(delay=new_delay)
        else:
            user_id = msg.header.get('user_id')
            message_text = msg.data.decode()
            try:
                with suppress(TelegramBadRequest):
                    await self.bot.send_message(user_id, message_text)
                await msg.ack()
            except TelegramRetryAfter:
                await msg.nak(delay=10)


# отключение консьюмера
async def unsubscribe(self) -> None:
    if self.stream_sub:
        await self.stream_sub.unsubscribe()
        logger.info('Consumer unsubscribed')
