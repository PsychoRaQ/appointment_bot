# аиограм
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select
# состояния
from app.fsm.user_states import UserAppointmentSG, UserNewAppointmentSG, FeedbackSG
# функции для работы с базой данных
from app.utils.database_func import get_slot_with_user_id
# сервисные функции
from app.utils.service_func import return_user_is_max_appointment


# Селектор диалогов из главного меню
# открывает следующие диалоги
async def user_dialog_selection(callback: CallbackQuery, widget: Select,
                                dialog_manager: DialogManager, data: str):
    match data:
        # создание новой записи, если не превышен лимит количества записей (стандартно - 2)
        # открываем нужное окно диалога, в зависимости от превышения лимита
        case 'make_new_appointment':
            result = await return_user_is_max_appointment(dialog_manager.middleware_data.get('session'),
                                                          callback.message.chat.id)
            if result or callback.message.chat.id in dialog_manager.middleware_data.get('admin_ids'):
                await dialog_manager.start(state=UserNewAppointmentSG.calendary_first_month, data={'for_admin': True},
                                           show_mode=ShowMode.AUTO)
            else:
                await dialog_manager.start(state=UserNewAppointmentSG.user_max_appointment, show_mode=ShowMode.AUTO)
        # просмотр всех существующих записей пользователя
        # открываем нужное окно диалога, в зависимости от наличия записей у пользователя
        case 'view_my_appointments':
            result = await get_slot_with_user_id(dialog_manager.middleware_data.get('session'),
                                                 callback.message.chat.id)
            if len(result) == 0:
                await dialog_manager.start(state=UserAppointmentSG.no_one_appointment, show_mode=ShowMode.AUTO)
            else:
                await dialog_manager.start(state=UserAppointmentSG.main, show_mode=ShowMode.AUTO)
        # окно обратной связи
        case 'user_feedback':
            await dialog_manager.start(state=FeedbackSG.feedback, show_mode=ShowMode.AUTO)
        case _:
            print(data)
