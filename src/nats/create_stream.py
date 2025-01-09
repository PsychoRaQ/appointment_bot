import asyncio

import nats
from nats.aio.client import Client
from nats.js.api import StreamConfig, RetentionPolicy
from nats.js.client import JetStreamContext


async def main():
    # Подключаемся к NATS серверу
    nc: Client = await nats.connect("nats://localhost:4222")
    # Получаем JetStream-контекст
    js: JetStreamContext = nc.jetstream()

    # Настройка стрима с заданными параметрами
    stream_config = StreamConfig(
        name="delayed_messages_aiogram",  # Название стрима
        subjects=[
            "aiogram.delayed.messages",
            "aiogram.dispatch.messages",
        ],
        retention=RetentionPolicy.WORK_QUEUE,  # Политика удержания
        max_bytes=300 * 1024 * 1024,  # 300 MiB
        max_msg_size=10 * 1024 * 1024,  # 10 MiB
        storage="file",  # Хранение сообщений на диске
        allow_direct=True,  # Разрешение получать сообщения без создания консьюмера
    )

    await js.add_stream(stream_config)

    print("Stream `delayed_messages_aiogram` created successfully.")


asyncio.run(main())
