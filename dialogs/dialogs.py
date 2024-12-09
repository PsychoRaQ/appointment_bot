from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Select, Group, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List

from dialogs.getters import (get_userdata, get_main_menu, get_user_appointments, get_free_dates_on_current_month,
                             get_free_dates_on_next_month, get_free_times_from_date, get_confirm_datetime)
from dialogs.handlers import (check_username, confirm_registration, correct_input, error_input, check_phone,
                              cancel_registration, go_next)
from dialogs.handlers import (user_dialog_selection)
from dialogs.handlers import (user_new_date_appointment, user_new_time_appointment)

from fsm.states import (MainMenuSG, StartSG, UserAppointmentSG, UserNewAppointmentSG)

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

# пользователь выбрал "Мои записи"
user_appointment_dialog = Dialog(
    Window(
        Const(text='Ваши записи:\n'),
        List(field=Format('{item[0]} - {item[1]}'),
             items='user_appointment'),
        Next(Const(text='Отменить запись'),
             id='next_button'),
        Cancel(Const(text='Назад'),
               id='cancel_button'),
        getter=get_user_appointments,
        state=UserAppointmentSG.main,
    ),
    Window(
        Const(text='Выберите запись для отмены:'),
        Cancel(Const(text='В главное меню'),
               id='cancel_button'),
        getter=get_user_appointments,
        state=UserAppointmentSG.delete_appointment,
    ),
)

# пользователь выбрал "Записаться"
user_new_appointment_dialog = Dialog(
    Window(
        Const(text='Выберите дату для записи:'),
        Button(Format(text='{current_month}'),
               id='month', ),
        Row(
            Button(Const(text='Пн'), id=''),
            Button(Const(text='Вт'), id=''),
            Button(Const(text='Ср'), id=''),
            Button(Const(text='Чт'), id=''),
            Button(Const(text='Пт'), id=''),
            Button(Const(text='Сб'), id=''),
            Button(Const(text='Вс'), id=''),
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
        Row(
            Button(Const(text='Пн'), id=''),
            Button(Const(text='Вт'), id=''),
            Button(Const(text='Ср'), id=''),
            Button(Const(text='Чт'), id=''),
            Button(Const(text='Пт'), id=''),
            Button(Const(text='Сб'), id=''),
            Button(Const(text='Вс'), id=''),
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
           )
)
