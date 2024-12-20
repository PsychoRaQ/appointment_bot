from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Select, Group, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List

from src.fsm.admin_states import AdminMenuSG, AdminEditCalendary, AdminAddNewUserAppointment

from src.admin_dialogs.getters import (get_admin_menu, get_free_dates_on_next_month, get_free_dates_on_current_month,
                                       get_free_times_from_date, slot_info_for_user)
from src.admin_dialogs.handlers import admin_dialog_selection
from src.admin_dialogs.handlers import admin_choose_date_for_edit, admin_choose_time_slot_for_edit, admin_close_slot

from src.services.service_func import get_weekday_button

'''
Все диалоги бота для администратора
'''

# Главное меню
main_menu_dialog = Dialog(
    Window(
        Const(text='~~~   Панель администрирования   ~~~'),
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
        Group(
            Select(
                Format('{item[0]}'),
                id='date',
                item_id_getter=lambda x: x[1],
                items='current_month_dates',
                on_click=admin_choose_date_for_edit,
            ),
            width=7
        ),
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
        Group(
            Select(
                Format('{item[0]}'),
                id='date',
                item_id_getter=lambda x: x[1],
                items='current_month_dates',
                on_click=admin_choose_date_for_edit,
            ),
            width=7
        ),
        Back(Format(text='◀️◀️◀️   {prev_month}   ◀️◀️◀️'),
             id='prev_month_button'),
        Cancel(Const(text='В главное меню'),
               id='cancel_button'),
        getter=get_free_dates_on_next_month,
        state=AdminEditCalendary.second_month,
    ),
    Window(
        Format(text='Изменение временных слотов на {text_date}:'),
        Group(
            Select(
                Format('{item[0]}'),
                id='time',
                item_id_getter=lambda x: x[1],
                items='open_time',
                on_click=admin_choose_time_slot_for_edit,
            ),
            width=4
        ),
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
                    'пользователь получит уведомление об отмене его записи.'),
        Button(Const(text='Подтвердить'), id='confirm_button', on_click=admin_close_slot),
        SwitchTo(Const(text='◀️ Назад'), id='b_button', state=AdminEditCalendary.first_month),
        getter=slot_info_for_user,
        state=AdminEditCalendary.user_on_date,
    ),
)

# диалог добавления новой записи администратором
# new_admin_appointment = Dialog(
#     Window(
#         Const(text='Выберите дату для записи пользователя:\n\n'
#                    'прим: отображены только открытые и свободные "слоты". Проверьте доступность нужных даты и времени перед записью.'),
#         Button(Format(text='{current_month}'),
#                id='month', ),
#         Row(
#             Button(Const(text='Пн'), id=''),
#             Button(Const(text='Вт'), id=''),
#             Button(Const(text='Ср'), id=''),
#             Button(Const(text='Чт'), id=''),
#             Button(Const(text='Пт'), id=''),
#             Button(Const(text='Сб'), id=''),
#             Button(Const(text='Вс'), id=''),
#         ),
#         Group(
#             Select(
#                 Format('{item[0]}'),
#                 id='date',
#                 item_id_getter=lambda x: x[1],
#                 items='current_month_dates',
#                 on_click=user_new_date_appointment,
#             ),
#             width=7
#         ),
#         Next(Format(text='▶️▶️▶️   {next_month}   ▶️▶️▶️'),
#              id='next_month_button'),
#         Cancel(Const(text='В главное меню'),
#                id='cancel_button'),
#         getter=get_free_dates_on_current_month,
#         state=AdminAddNewUserAppointment.first_month
#     ),
#     Window(
#         Const(text='Доступные даты для записи:'),
#         Button(Format(text='{current_month}'),
#                id='month', ),
#         Row(
#             Button(Const(text='Пн'), id=''),
#             Button(Const(text='Вт'), id=''),
#             Button(Const(text='Ср'), id=''),
#             Button(Const(text='Чт'), id=''),
#             Button(Const(text='Пт'), id=''),
#             Button(Const(text='Сб'), id=''),
#             Button(Const(text='Вс'), id=''),
#         ),
#         Group(
#             Select(
#                 Format('{item[0]}'),
#                 id='date',
#                 item_id_getter=lambda x: x[1],
#                 items='current_month_dates',
#                 on_click=user_new_date_appointment,
#             ),
#             width=7
#         ),
#         Back(Format(text='◀️◀️◀️   {prev_month}   ◀️◀️◀️'),
#              id='prev_month_button'),
#         Cancel(Const(text='В главное меню'),
#                id='cancel_button'),
#         getter=get_free_dates_on_next_month,
#         state=AdminAddNewUserAppointment.second_month,
#     ),
#
# ),
# )
