from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Select, Group, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List

# все геттеры прописаны в одном месте
from src.user_dialogs.getters import (get_userdata, get_main_menu, get_user_appointments,
                                      get_free_dates_on_current_month,
                                      get_free_dates_on_next_month, get_free_times_from_date, get_confirm_datetime)
# все состояния прописаны в одном месте
from src.fsm.user_states import (MainMenuSG, StartSG, UserAppointmentSG, UserNewAppointmentSG)

# хэндлеры для диалога регистрации
from src.user_dialogs.handlers import (check_username, confirm_registration, correct_input, error_input, check_phone,
                                       cancel_registration, go_next)
# хэндлеры для диалога-селектора в главном меню
from src.user_dialogs.handlers import (user_dialog_selection)
# хэндлеры для диалога записи пользователя
from src.user_dialogs.handlers import (user_new_date_appointment, user_new_time_appointment)
# хэндлеры для диалога удаления записей
from src.user_dialogs.handlers import (user_delete_appointment, user_is_confirm_delete_appointment)

from src.services.service_func import get_weekday_button

'''
Все диалоги бота
Возможно, потом нужно перенести текстовую часть в другое место
'''

# Диалог регистрации пользователя
start_dialog = Dialog(
    Window(
        Const('Добро пожаловать!\nПеред тем как записаться, нужно пройти регистрацию'),
        Next(Const('Зарегистрироваться'), id='b_next'),
        getter=get_userdata,
        state=StartSG.start
    ),
    Window(
        Const(
            'Давайте познакомимся?\nПожалуйста, отправьте в чат Ваше имя.\n(Не более 10 символов)\n\nЕсли хотите взять Ваше имя из телеграмма - просто нажмите "Продолжить"'),
        TextInput(
            id='name_input',
            type_factory=check_username,
            on_success=correct_input,
            on_error=error_input,
        ),
        Row(
            Back(Const('◀️ Назад'), id='b_back'),
            Button(Const('Продолжить ▶️'), id='b_next_username', on_click=go_next),
        ),
        getter=get_userdata,
        state=StartSG.get_name,
    ),
    Window(
        Format(
            'Отлично, {username}!\n Пожалуйста, отправьте в чат свой номер телефона для связи\n(на всякий случай)\n\nПримечание: Вы можете ввести свой номер в любом формате (8, +7, 7)'),
        TextInput(
            id='phone_input',
            type_factory=check_phone,
            on_success=correct_input,
            on_error=error_input,
        ),
        Back(Const('◀️ Назад'), id='b_back'),
        getter=get_userdata,
        state=StartSG.get_phone
    ),
    Window(
        Format('Пожалуйста, проверьте Ваши данные.\nИмя: {username}\nТелефон: {phone}\n\nВсе верно?'),
        Button(Const('Подтвердить регистрацию'), id='b_confirm', on_click=confirm_registration),
        Button(Const('Пройти регистрацию сначала'), id='b_cancel', on_click=cancel_registration),
        getter=get_userdata,
        state=StartSG.confirm
    ),
    getter=get_userdata,
)

# Главное меню
main_menu_dialog = Dialog(
    Window(
        Const(text='~~~   Главное меню   ~~~'),
        Group(
            Select(
                Format('{item[0]}'),
                id='main_menu',
                item_id_getter=lambda x: x[1],
                items='main_menu',
                on_click=user_dialog_selection,
            ),
            width=2
        ),
        state=MainMenuSG.main_menu,
        getter=get_main_menu,
    ),
)

# пользователь выбрал "Мои записи" (+ отмена записей)
user_appointment_dialog = Dialog(
    Window(
        Const(text='Ваши записи:\n'),
        List(field=Format('{item[0]} - {item[1]}'),
             items='user_appointment'),
        Next(Const(text='Отменить запись'),
             id='next_button'),
        Cancel(Const(text='◀️ Назад'),
               id='cancel_button'),
        getter=get_user_appointments,
        state=UserAppointmentSG.main,
    ),
    Window(
        Const(text='Выберите запись для отмены:'),
        Group(
            Select(
                Format('❌ {item[0]} - {item[1]} ❌'),
                id='datetime',
                item_id_getter=lambda x: f'{x[0]}-{x[1]}',
                items='user_appointment',
                on_click=user_delete_appointment,
            ),
            width=1,
        ),
        Back(Const(text='◀️ Назад'),
             id='back_button'),
        getter=get_user_appointments,
        state=UserAppointmentSG.delete_appointment_datetime,
    ),
    Window(
        Format(text='Вы точно хотите отменить свою запись на {datetime_for_user}:'),
        Button(text=Const('Подтвердить отмену'), id='del_conf_bnt', on_click=user_is_confirm_delete_appointment),
        Back(Const(text='◀️ Назад'),
             id='back_button'),
        getter=get_user_appointments,
        state=UserAppointmentSG.delete_appointment_confirm,
    ),
    Window(
        Format(text='Ваша запись на {datetime_for_user} была отменена.'),
        Cancel(Const(text='В главное меню'),
               id='back_button'),
        getter=get_user_appointments,
        state=UserAppointmentSG.delete_appointment_result,
    ),
    Window(
        Const(text='Записи не найдены.\nЧтобы записаться нажмите кнопку "Записаться" в главном меню бота.'),
        Cancel(Const(text='Главное меню'),
               id='cancel_button'),
        state=UserAppointmentSG.no_one_appointment,
    ),
)

# пользователь выбрал "Записаться"
user_new_appointment_dialog = Dialog(
    Window(
        Const(text='Выберите дату для записи:'),
        Button(Format(text='{current_month}'),
               id='month', ),
        Row(
            *get_weekday_button()
        ),
        Group(
            Select(
                Format('{item[0]}'),
                id='date',
                item_id_getter=lambda x: x[1],
                items='current_month_dates',
                on_click=user_new_date_appointment,
            ),
            width=7
        ),
        Next(Format(text='▶️▶️▶️   {next_month}   ▶️▶️▶️'),
             id='next_month_button'),
        Cancel(Const(text='В главное меню'),
               id='cancel_button'),
        getter=get_free_dates_on_current_month,
        state=UserNewAppointmentSG.calendary_first_month
    ),
    Window(
        Const(text='Доступные даты для записи:'),
        Button(Format(text='{current_month}'),
               id='month', ),
        Row(*get_weekday_button()),
        Group(
            Select(
                Format('{item[0]}'),
                id='date',
                item_id_getter=lambda x: x[1],
                items='current_month_dates',
                on_click=user_new_date_appointment,
            ),
            width=7
        ),
        Back(Format(text='◀️◀️◀️   {prev_month}   ◀️◀️◀️'),
             id='prev_month_button'),
        Cancel(Const(text='В главное меню'),
               id='cancel_button'),
        getter=get_free_dates_on_next_month,
        state=UserNewAppointmentSG.calendary_second_month,
    ),
    Window(
        Format(text='Доступное время для записи на {date}:'),
        Group(
            Select(
                Format('{item[0]}'),
                id='time',
                item_id_getter=lambda x: x[0],
                items='open_time',
                on_click=user_new_time_appointment,
            ),
            width=4
        ),
        SwitchTo(Const(text='◀️ Назад'), id='b_button', state=UserNewAppointmentSG.calendary_first_month),

        getter=get_free_times_from_date,
        state=UserNewAppointmentSG.choose_time,
    ),
    Window(
        Format(text='Вы успешно записались на {date} - {time}!\n\n'
                    'Чтобы посмотреть список своих записей или отменить запись, выберите пункт "Мои записи" в главном меню.'),
        Cancel(Const(text='Главное меню'), id='cancel_button'),
        state=UserNewAppointmentSG.confirm_datetime,
        getter=get_confirm_datetime,
    ),
    Window(Format(text='Произошла ошибка во время записи на {date} - {time}!\n'
                       'Пожалуйста, попробуйте позже или выберите другое время.'),
           Cancel(Const(text='Главное меню'), id='cancel_button'),
           state=UserNewAppointmentSG.error_confirm,
           getter=get_confirm_datetime,
           ),
    Window(
        Const(
            text='Вы записаны максимальное количество раз.\nЧтобы изменить время записи, пожалуйста, отмените одну из Ваших записей.\n\n'
                 '(Мои записи -> отменить запись)'),
        Cancel(Const(text='Главное меню'),
               id='cancel_button'),
        state=UserNewAppointmentSG.user_max_appointment,
    ),
)
