# КОНФИГ БОТА

from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    dsn: str
    is_echo: bool


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_id: list  # Список id администраторов бота


# Создаем конфиг из переменных указанных в env по пути path
def load_config(path: str | None = None) -> TgBot:
    env: Env = Env()
    env.read_env(path)

    return TgBot(
        token=env('BOT_TOKEN'),
        admin_id=[int(i) for i in env.list('ADMIN_IDS') if i != ''],
    )


# Конфигурация для подключения к базе данных
def load_database(path: str | None = None) -> DatabaseConfig:
    env: Env = Env()
    env.read_env(path)

    dsn = env('DATABASE_DSN')

    return DatabaseConfig(dsn=dsn, is_echo=False)
