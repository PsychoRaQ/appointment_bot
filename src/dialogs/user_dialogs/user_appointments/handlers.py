# аиограм
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select
# функции для работы с базой данных
from src.services.database_func import user_confirm_datetime, user_is_register, get_slot_from_db
# сервисные функции
from src.services.service_func import datetime_format


# пользователь выбрал "слот" для отмены
# собираем все нужные данные "слота" и переходим к окну подтверждения отмены записи
async def user_choose_slot_for_delete(callback: CallbackQuery, widget: Select,
                                      dialog_manager: DialogManager, data: str):
    # форматируем данные "слота" для дальнейшей работы
    date, time = data.split('-')
    date = date.replace('.', '-')
    date, text_date, time, text_time = await datetime_format(date, time)

    session = dialog_manager.middleware_data.get('session')
    role = dialog_manager.middleware_data.get('user_role')

    admin_id = dialog_manager.dialog_data.get('admin_id')
    if not admin_id:
        if role == 'admin':
            admin_id = callback.message.chat.id
        else:
            user = await user_is_register(session, callback.message.chat.id)
            admin_id = user.admin_id
        await dialog_manager.update({'admin_id': admin_id})
    slot = await get_slot_from_db(date, time, admin_id, session)
    comment = slot.comment
    await dialog_manager.update({'text_date': text_date, 'text_time': text_time, 'comment': comment})
    await dialog_manager.next(show_mode=ShowMode.EDIT)


# пользователь подтвердил отмену выбранного слота
async def user_is_confirmed_delete_appointment(callback: CallbackQuery, widget: Select,
                                             dialog_manager: DialogManager):
    user_id = callback.message.chat.id
    session = dialog_manager.middleware_data.get('session')
    text_date = dialog_manager.dialog_data.get('text_date')
    text_time = dialog_manager.dialog_data.get('text_time')
    date, text_date, time, text_time = await datetime_format(text_date, text_time)
    admin_id = dialog_manager.dialog_data.get('admin_id')
    role = dialog_manager.middleware_data.get('user_role')
    user = await user_is_register(session, user_id)
    bot = dialog_manager.middleware_data.get('bot')
    status = 'delete'

    # отменяем запись пользователя в базе, делаем "слот" доступным для записи другим пользователям
    await user_confirm_datetime(user_id, date, time, status, admin_id, session)

    # отправляем в бакет метаданные о состоянии "слота" (отмена отложенного уведомления)
    message_id = text_date + text_time
    kv = dialog_manager.middleware_data.get('storage')
    await kv.put(str(message_id), b'0')

    # если пользователь отменил свою запись - отправляем уведомление об этом админу, к которому "привязан" пользователь
    if role == 'user':
        try:
            await bot.send_message(admin_id,
                                   f'Пользователь {user.username} отменил свою запись {text_date} - {text_time}\n'
                                   f'Телефон: {user.phone}')
        except Exception as e:
            print(e)

    await dialog_manager.next(show_mode=ShowMode.EDIT)
