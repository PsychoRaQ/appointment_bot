
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from keyboards.calendary_kb import create_calendary_kb, create_times_kb

from lexicon.lexicon import LEXICON, DATE_LST

from filters.filters import DateTimeIsCorrect

from services.service_func import change_datetime_status

router = Router()


@router.message(CommandStart())
async def proccess_start_command(message: Message):
    await message.answer(LEXICON['/start'])


@router.message(Command(commands='help'))
async def proccess_help_command(message: Message):
    await message.answer(LEXICON['/help'])


@router.message(Command(commands='beginning'))
async def proccess_beginning_command(message: Message):
    await message.answer(LEXICON['/beginning'])


@router.message(Command(commands='calendary'))
async def proccess_calendary_command(message: Message):
    keyboard = create_calendary_kb(7, **DATE_LST)
    await message.answer(text='Календарь',
                         reply_markup=keyboard)


@router.callback_query(F.data.in_(DATE_LST))
async def process_date_is_confirm(callback: CallbackQuery):
    keyboard = create_times_kb(5, DATE_LST[callback.data])
    await callback.message.edit_text(text='Время:',
                                     reply_markup=keyboard)

@router.callback_query(DateTimeIsCorrect())
async def process_datetime_is_choose(callback: CallbackQuery):
    await change_datetime_status(callback.data)
    await callback.message.edit_text(
        text=f'Отлично! Вы записаны на {callback.data}!',
        show_alert=True,
        reply_markup=None
    )

@router.callback_query()
async def process_datetime_is_choose(callback: CallbackQuery):
    print('callback.data')
    await callback.answer()