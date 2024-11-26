from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from lexicon.lexicon import DATE_LST

class DateTimeIsCorrect(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        date, time = callback.data.split(',')

        return date in DATE_LST and DATE_LST[date].times[time].lock is False
