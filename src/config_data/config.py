# УСТАРЕВШИЙ КУСОК КОДА ВИСИТ ДО НОВОЙ БД


# Токен бота
BOT_TOKEN = '7264027636:AAENChZiBfo7nMSHHGhyIacTdxs82HqjXUA'
# Текст для команды /help (вынес сюда, т.к. этот файл должен заполнять "заказчик")
HELP_COMMAND_DESCRIPTION = 'Здесь описание бота'
DATABASE_PATH = 'database/bot_database.db'

# КОНФИГ БОТА

from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str  # Название базы данных
    db_host: str  # URL-адрес базы данных
    db_user: str  # Username пользователя базы данных
    db_password: str  # Пароль к базе данных


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_id: str  # Список id администраторов бота


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig

# Создаем конфиг из переменных указанных в env по пути path
def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_id=env('GRAND_ADMIN_ID'),
        ),
        db=DatabaseConfig(
            database=env('DATABASE'),
            db_host=env('DB_HOST'),
            db_user=env('DB_USER'),
            db_password=env('DB_PASSWORD'),
        )
    )
