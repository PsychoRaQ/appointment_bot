import logging
from datetime import datetime, timedelta, timezone
from aiogram import Bot
from nats.aio.client import Client
from nats.aio.msg import Msg
from nats.js import JetStreamContext

logger = logging.getLogger(__name__)

'''
консьюмер системы подписки
'''


class SubscribeConsumer:
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
        self.kv_storage = await self.js.key_value(bucket='subscribe_storage')

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
            user_id = msg.headers.get('user_id')
            data = await self.kv_storage.get(user_id)
            days = int(data.value.decode("utf-8"))
            if days == 3 or days == 1:
                date = datetime.strftime(datetime.today() + timedelta(days=days), '%d-%m-%Y')
                await self.bot.send_message(user_id,
                                            f'Уважаемый администратор, напоминаем что срок Вашей подписки заканчивается {date}.\n'
                                            f'Не забудьте продлить подписку, чтобы продолжать пользоваться ботом.')
            if days > 0:
                data = bytes(str(days - 1), encoding="utf-8")
                await self.kv_storage.put(user_id, data)
                await msg.nak(delay=3600)
            else:
                await self.bot.send_message(user_id,
                                            f'Уважаемый администратор, Ваша подписка была приостановлена.\n'
                                            f'Чтобы продолжать пользоваться ботом, пожалуйста, оплатите подписку.')
                await msg.ack()


# отключение консьюмера
async def unsubscribe(self) -> None:
    if self.stream_sub:
        await self.stream_sub.unsubscribe()
        logger.info('Consumer unsubscribed')
