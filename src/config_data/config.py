# УСТАРЕВШИЙ КУСОК КОДА ВИСИТ ДО НОВОЙ БД


# Токен бота
BOT_TOKEN = '7264027636:AAENChZiBfo7nMSHHGhyIacTdxs82HqjXUA'
# Текст для команды /help (вынес сюда, т.к. этот файл должен заполнять "заказчик")
HELP_COMMAND_DESCRIPTION = 'Здесь описание бота'
DATABASE_PATH = 'db/bot_database.db'

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
    admin_id: str  # Список id администраторов бота


#
# @dataclass
# class Config:
#     tg_bot: TgBot
#     db: DatabaseConfig


# Создаем конфиг из переменных указанных в env по пути path
def load_config(path: str | None = None) -> TgBot:
    env: Env = Env()
    env.read_env(path)

    return TgBot(
        token=env('BOT_TOKEN'),
        admin_id=env('GRAND_ADMIN_ID')
    )

# Конфигурация для подключения к базе данных
def load_database(path: str | None = None) -> DatabaseConfig:
    env: Env = Env()
    env.read_env(path)

    dsn = env('DATABASE_DSN')

    return DatabaseConfig(dsn=dsn, is_echo=False)
