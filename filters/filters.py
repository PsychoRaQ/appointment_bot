from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from services.database_func import (user_is_sign, check_user_phone, get_datetime_from_db, user_is_admin)
from services import database_func


class DateTimeIsCorrect(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        if ',' in callback.data:
            date, time = callback.data.split(',')
            db = database_func.get_two_slots_where('is_locked', False, 'user_id', False, 'date, time')

            for slot in db:
                if date in slot and time in slot:
                    return True
        else:
            return False


class DateIsCorrect(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            date = callback.data
            db = database_func.get_two_slots_where('is_locked', False, 'user_id', False, 'date')
            for slot in db:
                if date in slot:
                    return True
        except Exception as e:
            print(e)
            return False


# Проверяем наличие "контакта" в сообщении
class MessageContact(BaseFilter):
    async def __call__(self, message) -> bool:
        return message.contact


class UserIsRegister(BaseFilter):
    async def __call__(self, message) -> bool:
        return user_is_sign(message.from_user.id)


class UserIsDeleteAppointment(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            cb_username, cb_date = callback.data.split('_delete_')
            return callback.data == f'{callback.message.chat.id}_delete_{cb_date}'
        except:
            return False


class UserIsDeleteAppointmentTime(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            cb_username, cb_date, cb_time = callback.data.split('_delete_')
            return callback.data == f'{callback.message.chat.id}_delete_{cb_date}_delete_{cb_time}'
        except:
            return False


class UserIsGeneralAdmin(BaseFilter):
    async def __call__(self, message) -> bool:
        return user_is_sign(str(message.from_user.id)) and user_is_admin(str(message.from_user.id)) == 2


class UserIsAdmin(BaseFilter):
    async def __call__(self, message) -> bool:
        return user_is_sign(str(message.from_user.id)) and user_is_admin(str(message.from_user.id))


class AdminChooseDate(BaseFilter):
    async def __call__(self, callback) -> bool:
        try:
            cb_date, is_admin = callback.data.split('_')
            return callback.data == f'{cb_date}_admin' and ',' not in cb_date
        except:
            return False


class AdminChooseTime(BaseFilter):
    async def __call__(self, callback) -> bool:
        try:
            cb_date, is_admin = callback.data.split('_')
            return callback.data == f'{cb_date}_admin' and ',' in cb_date
        except:
            return False
