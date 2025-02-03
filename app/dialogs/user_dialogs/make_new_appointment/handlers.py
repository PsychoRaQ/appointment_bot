# аиограм
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Select
# состояния
from app.fsm.user_states import UserNewAppointmentSG
# паблишер для отправки отложенных уведомлений
from app.services.nats_service.publishers.publishers import send_delay_message_publisher
# функции для работы с базой данных
from app.utils.database_func import user_confirm_datetime
# сервисные функции
from app.utils.service_func import datetime_format
# datetime
from datetime import datetime


# Пользователь выбрал дату для записи
async def choose_date_for_appointment(callback: CallbackQuery, widget: Select,
                                      dialog_manager: DialogManager, data: str):
    if data != 'locked':
        await dialog_manager.update({'date': data})
        await dialog_manager.switch_to(state=UserNewAppointmentSG.choose_time, show_mode=ShowMode.AUTO)


# Пользователь выбрал время для записи
async def choose_time_for_appointment(callback: CallbackQuery, widget: Select,
                                      dialog_manager: DialogManager, data: str):
    if data:
        await dialog_manager.update({'time': data})
        # проверка на роль пользователя
        # если админ - переходим к написанию комментария
        role = dialog_manager.middleware_data.get('user_role')
        if role == 'admin':
            await dialog_manager.switch_to(state=UserNewAppointmentSG.write_admin_comment, show_mode=ShowMode.AUTO)
        else:
            # пользователь занимает выбранный "слот"
            session = dialog_manager.middleware_data.get('session')
            status = 'confirm'
            date, text_date, time, text_time = await datetime_format(date=dialog_manager.dialog_data.get('date'),
                                                                     time=data)
            admin_id = dialog_manager.dialog_data.get('admin_id')
            result = await user_confirm_datetime(callback.message.chat.id, date, time, status, admin_id, session)

            # настройка отложенного уведомления пользователю (за 24ч до записи)
            timestamp = datetime.now()
            time_to_send_notification = datetime.combine(date, time)
            delay = int((time_to_send_notification - timestamp).total_seconds()) - 3600 * 24
            js = dialog_manager.middleware_data.get('js')
            subject = dialog_manager.middleware_data.get('delay_del_subject')
            message_id = text_date + text_time

            # добавляем метаданные сообщения в бакет
            kv = dialog_manager.middleware_data.get('storage')
            await kv.put(f'{message_id}', bytes(str(callback.message.chat.id), encoding='utf-8'))

            # отправляем сообщение в натс
            await send_delay_message_publisher(
                js=js,
                subject=subject,
                delay=delay,
                message_id=message_id,
                date=text_date,
                time=text_time,
            )
            # в зависимости от результата выполнения записи в базу, отображаем нужное окно диалога
            if result:
                await dialog_manager.switch_to(state=UserNewAppointmentSG.confirm_datetime, show_mode=ShowMode.AUTO)
            else:
                await dialog_manager.switch_to(state=UserNewAppointmentSG.error_confirm, show_mode=ShowMode.AUTO)


# Подтверждение "ручной записи"
async def make_admin_comment(callback: CallbackQuery, widget: Select,
                             dialog_manager: DialogManager):
    session = dialog_manager.middleware_data.get('session')
    status = 'confirm'
    date, text_date, time, text_time = await datetime_format(date=dialog_manager.dialog_data.get('date'),
                                                             time=dialog_manager.dialog_data.get('time'))
    comment = dialog_manager.dialog_data.get('comment')
    admin_id = callback.message.chat.id
    # в зависимости от результата выполнения записи в базу, отображаем нужное окно диалога
    result = await user_confirm_datetime(admin_id, date, time, status, admin_id, session, comment)
    if result:
        await dialog_manager.switch_to(state=UserNewAppointmentSG.confirm_admin_datetime, show_mode=ShowMode.AUTO)
    else:
        await dialog_manager.switch_to(state=UserNewAppointmentSG.error_confirm, show_mode=ShowMode.AUTO)


# Админ ввел комментарий к "ручной записи"
async def confirmed_admin_appointment(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    await dialog_manager.update({'comment': text})
    await dialog_manager.next(show_mode=ShowMode.EDIT)


# обработчик кнопки "назад" в окне ввода комментария администратора
async def back_btn_adm_appointment(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager) -> None:
    await dialog_manager.switch_to(UserNewAppointmentSG.choose_time)
