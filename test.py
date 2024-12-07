from datetime import datetime, date

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, User, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.text import Format
from config_data.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class StartSG(StatesGroup):
    start = State()


from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Select, Row, Group, Calendar
from services import database_func


async def on_date_selected(callback: CallbackQuery, widget,
                           manager: DialogManager, selected_date: date):
    await callback.answer(str(selected_date))


async def username_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    dates = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
    data = database_func.get_two_slots_where('is_locked', False, 'user_id', False, '*')
    data_lst = []
    for i in data:
        day = i[1].split('-')
        day = f'{day[2]}.{day[1]}'
        if day not in data_lst:
            data_lst.append(day)
    data_lst.sort()
    getter_data = {'dates': dates, 'data': data_lst}
    return getter_data


start_dialog = Dialog(
    Window(
        Const(text='Календарь'),
        Group(Select(
            Format('{item}'),
            id='data',
            item_id_getter=lambda x: x,
            items='data'
        ),
            width=7),

        state=StartSG.start,
        getter=username_getter,
    ),
)


@dp.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    dp.include_router(start_dialog)
    setup_dialogs(dp)
    dp.run_polling(bot)
