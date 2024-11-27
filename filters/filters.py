from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery
from services.database_func import (check_user_is_sign,check_user_phone, get_datetime_from_db, user_is_admin)

class DateTimeIsCorrect(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        try:
            date, time = callback.data.split(',')
            db = get_datetime_from_db()
            return db[date][time]['lock'] is False
        except:
            return False

class MessageContact(BaseFilter):
    async def __call__(self, message) -> bool:
        return message.contact


class UserIsRegister(BaseFilter):
    async def __call__(self, message) -> bool:
        return check_user_is_sign(str(message.from_user.id)) and check_user_phone(str(message.from_user.id))


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
        return check_user_is_sign(str(message.from_user.id)) and user_is_admin(str(message.from_user.id)) == 2

class UserIsAdmin(BaseFilter):
    async def __call__(self, message) -> bool:
        return check_user_is_sign(str(message.from_user.id)) and user_is_admin(str(message.from_user.id))

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
