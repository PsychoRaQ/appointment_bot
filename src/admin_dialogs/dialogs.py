from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Select, Group, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List
# импорт состояний
from src.fsm.admin_states import AdminMenuSG, AdminEditCalendary, AllAppointments
# импорт сервисных функций-билдеров
from src.services.widget_builder_for_dialogs import get_weekday_button, get_group
# импорт всех геттеров
from src.admin_dialogs.getters import (get_admin_menu, get_free_dates_on_next_month, get_free_dates_on_current_month,
                                       get_free_times_from_date, slot_info_for_user, get_all_slots)
# хэндлеры для редактирования расписания
from src.admin_dialogs.handlers import admin_choose_date_for_edit, admin_choose_time_slot_for_edit, admin_close_slot
# хэндлеры для селектора (главное меню)
from src.admin_dialogs.handlers import admin_dialog_selection
# хэндлер для отображения всех записей
from src.admin_dialogs.handlers import admin_choose_date_for_look

'''
Все диалоги бота для администратора
(для функции ручной записи и удаления ручной записи используются пользовательские диалоги)
'''

# Главное меню
main_menu_dialog = Dialog(
    Window(
        Const(text='~~   Панель администрирования  ~~'),
        Group(
            Select(
                Format('{item[0]}'),
                id='main_menu',
                item_id_getter=lambda x: x[1],
                items='main_menu',
                on_click=admin_dialog_selection,
            ),
            width=1
        ),
        state=AdminMenuSG.admin_menu,
        getter=get_admin_menu,
    ),
)

# диалог настройки расписания
edit_calendary = Dialog(
    Window(
        Const(text='Выберите дату для изменения расписания:'),
        Button(Format(text='{current_month}'),
               id='month', ),
        Row(*get_weekday_button()),
        get_group(admin_choose_date_for_edit, 'date'),  # group, основная часть календаря
        Next(Format(text='▶️▶️▶️   {next_month}   ▶️▶️▶️'),
             id='next_month_button'),
        Cancel(Const(text='В главное меню'),
               id='cancel_button'),
        getter=get_free_dates_on_current_month,
        state=AdminEditCalendary.first_month
    ),
    Window(
        Const(text='Выберите дату для изменения расписания:'),
        Button(Format(text='{current_month}'),
               id='month', ),
        Row(*get_weekday_button()),
        get_group(admin_choose_date_for_edit, 'date'),  # group, основная часть календаря
        Back(Format(text='◀️◀️◀️   {prev_month}   ◀️◀️◀️'),
             id='prev_month_button'),
        Cancel(Const(text='В главное меню'),
               id='cancel_button'),
        getter=get_free_dates_on_next_month,
        state=AdminEditCalendary.second_month,
    ),
    Window(
        Format(text='Изменение временных слотов на {text_date}:'),
        get_group(admin_choose_time_slot_for_edit, 'time'),  # group, отображение слотов
        SwitchTo(Const(text='◀️ Назад'), id='b_button', state=AdminEditCalendary.first_month),
        Cancel(Const(text='Главное меню'), id='cancel_button'),
        getter=get_free_times_from_date,
        state=AdminEditCalendary.choose_time,
    ),
    Window(
        Format(text='Внимание: на {text_date} - {text_time} записан пользователь.\n'
                    'Имя: {username}\n'
                    'Телефон: {phone}\n\n'
                    'Если Вы все-таки хотите закрыть слот - нажмите кнопку "Подтвердить". В таком случае, '
                    'пользователь получит уведомление об отмене его записи.', when=~F['is_admin']),
        Format(text='Внимание: на {text_date} - {text_time} пользователь был записан администратором.\n'
                    'Комментарий администратора: {comment}\n\n'
                    'Если Вы все-таки хотите закрыть слот - нажмите кнопку "Подтвердить".', when=F['is_admin']),
        Button(Const(text='Подтвердить'), id='confirm_button', on_click=admin_close_slot),
        SwitchTo(Const(text='◀️ Назад'), id='b_button', state=AdminEditCalendary.first_month),
        getter=slot_info_for_user,
        state=AdminEditCalendary.user_on_date,
    ),
)

# Просмотр всех доступных слотов
all_appointments = Dialog(
    Window(
        Const(text='Выберите дату для просмотра всех доступных слотов:'),
        Button(Format(text='{current_month}'),
               id='month', ),
        Row(*get_weekday_button()),
        get_group(admin_choose_date_for_look, 'date'),  # group, основная часть календаря
        Next(Format(text='▶️▶️▶️   {next_month}   ▶️▶️▶️'),
             id='next_month_button'),
        Cancel(Const(text='В главное меню'),
               id='cancel_button'),
        getter=get_free_dates_on_current_month,
        state=AllAppointments.first_month
    ),
    Window(
        Const(text='Выберите дату для просмотра всех доступных слотов:'),
        Button(Format(text='{current_month}'),
               id='month', ),
        Row(*get_weekday_button()),
        get_group(admin_choose_date_for_look, 'date'),  # group, основная часть календаря
        Back(Format(text='◀️◀️◀️   {prev_month}   ◀️◀️◀️')),
        Cancel(Const(text='В главное меню'),
               id='cancel_button'),
        getter=get_free_dates_on_next_month,
        state=AllAppointments.second_month
    ),
    Window(
        Format(text='Расписание {date}:\n'),
        List(field=Format('{item}'),
             items='slot'),
        SwitchTo(Const(text='◀️ Назад'), id='b_button', state=AllAppointments.first_month),
        getter=get_all_slots,
        state=AllAppointments.appointments_list
    ),
)
