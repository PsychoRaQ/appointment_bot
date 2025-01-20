# КОНФИГ БОТА

from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    dsn: str  # url подключения к базе данных
    is_echo: bool


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_id: list  # Список id администраторов бота
    description: str | list  # описание бота/помощь
    admin_url: str  # ссылка на тг админа для обратной связи


@dataclass
class NatsConfig:
    servers: list[str]


@dataclass
class NatsDelayedConsumerConfig:
    subject: str
    stream: str
    durable_name: str


@dataclass
class Nats:
    nats: NatsConfig
    delayed_consumer: NatsDelayedConsumerConfig
    dispatch_consumer: NatsDelayedConsumerConfig
    subscribe_consumer: NatsDelayedConsumerConfig


def load_nats(path: str | None = None):
    env: Env = Env()
    env.read_env(path)
    return Nats(
        nats=NatsConfig(servers=env.list('NATS_SERVERS')),
        delayed_consumer=NatsDelayedConsumerConfig(
            subject=env('NATS_DELAYED_CONSUMER_SUBJECT'),
            stream=env('NATS_DELAYED_CONSUMER_STREAM'),
            durable_name=env('NATS_DELAYED_CONSUMER_DURABLE_NAME')
        ),
        dispatch_consumer=NatsDelayedConsumerConfig(
            subject=env('NATS_DISPATCH_CONSUMER_SUBJECT'),
            stream=env('NATS_DELAYED_CONSUMER_STREAM'),
            durable_name=env('NATS_DISPATCH_CONSUMER_DURABLE_NAME')
        ),
        subscribe_consumer=NatsDelayedConsumerConfig(
            subject=env('NATS_SUBSCRIBE_CONSUMER_SUBJECT'),
            stream=env('NATS_DELAYED_CONSUMER_STREAM'),
            durable_name=env('NATS_SUBSCRIBE_CONSUMER_DURABLE_NAME')
        )
    )

    # Создаем конфиг из переменных указанных в env по пути path


def load_config(path: str | None = None) -> TgBot:
    env: Env = Env()
    env.read_env(path)

    return TgBot(
        token=env('BOT_TOKEN'),
        admin_id=[int(i) for i in env.list('ADMIN_IDS') if i != ''],
        description=env('HELP_COMMAND_DESCRIPTION'),
        admin_url=env('ADMIN_TG_URL'),
    )


# Конфигурация для подключения к базе данных
def load_database(path: str | None = None) -> DatabaseConfig:
    env: Env = Env()
    env.read_env(path)

    dsn = env('DATABASE_DSN')

    return DatabaseConfig(dsn=dsn, is_echo=False)
