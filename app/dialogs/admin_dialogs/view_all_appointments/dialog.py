# аиограм
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List
# импорт состояний
from app.fsm.admin_states import AllAppointments
# импорт сервисных функций-билдеров
from app.utils.widget_builder_for_dialogs import get_weekday_button, get_group
# геттеры
from app.dialogs.user_dialogs.make_new_appointment.getters import get_free_dates
from app.dialogs.admin_dialogs.view_all_appointments.getters import get_all_slots
# хэндлеры
from app.dialogs.admin_dialogs.view_all_appointments.handlers import admin_choose_view_date

'''
Диалог для просмотра админом всех открытых им "слотов".
Админ выбирает дату, после чего ему отображаются данные "слотов" в виде списка.
'''

# Просмотр всех доступных слотов
view_all_appointments_dialog = Dialog(
    # календарь с выбором даты на текущий месяц
    Window(
        Const(text='Выберите дату для просмотра всех доступных слотов:'),
        Button(Format(text='{current_month}'), id='month'),
        Row(*get_weekday_button()),  # дни недели
        get_group(admin_choose_view_date, 'date', 'current_month'),  # group, основная часть календаря
        Next(Format(text='{next_month}   →')),
        Cancel(Const(text='☰ Главное меню')),
        getter=get_free_dates,
        state=AllAppointments.first_month
    ),
    # календарь с выбором даты на следующий месяц
    Window(
        Const(text='Выберите дату для просмотра всех доступных слотов:'),
        Button(Format(text='{next_month}'),
               id='month', ),
        Row(*get_weekday_button()),  # дни недели
        get_group(admin_choose_view_date, 'date', 'next_month'),  # group, основная часть календаря
        Back(Format(text='←   {current_month}')),
        Cancel(Const(text='☰ Главное меню')),
        getter=get_free_dates,
        state=AllAppointments.second_month
    ),
    # окно со списком всех открытых "слотов" на выбранную дату
    Window(
        Format(text='Расписание {date}:\n'),
        List(field=Format('{item}'),
             items='slot'),
        SwitchTo(Const(text='← Назад'), id='b_back', state=AllAppointments.first_month),
        getter=get_all_slots,
        state=AllAppointments.appointments_list
    ),
)
