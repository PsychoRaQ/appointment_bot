# аиограм
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
# состояния
from app.fsm.user_states import UserNewAppointmentSG
# билдеры для инлайн клавиатур
from app.utils.widget_builder_for_dialogs import get_weekday_button, get_group
# геттеры
from app.dialogs.user_dialogs.make_new_appointment.getters import (get_free_dates, get_free_times_from_date,
                                                                   get_confirm_datetime)
# хэндлеры
from app.dialogs.user_dialogs.make_new_appointment.handlers import (choose_time_for_appointment,
                                                                    choose_date_for_appointment, make_admin_comment,
                                                                    confirmed_admin_appointment,
                                                                    back_btn_adm_appointment)

'''
Диалог создания новой записи пользователем.
Пользователь выбирает открытую дату и временной "слот" на эту дату.
После записи "слот" закрепляется за пользователем и становится недоступен для
отображения и записи остальным пользователям.
Во время записи создается отложенное уведомление (сообщение-напоминалка за 24ч до записи).

Календари с датами генерируются автоматически в момент открытия нужного окна диалога.
- Для выбора доступен текущий месяц и следующий.
- Даты в календаре доступны начиная с "сегодняшнего дня" и далее.

Диалог используется админами для функции "Ручной записи", для этого добавлены дополнительные стейты
'''

make_appointment_dialog = Dialog(
    # отображение календаря с датами на текущий месяц
    Window(
        Const(text='Выберите дату для записи:'),
        Button(Format(text='{current_month}'), id='month'),
        Row(*get_weekday_button()),  # дни недели
        get_group(choose_date_for_appointment, 'date', 'current_month'),  # group, основная часть календаря
        Next(Format(text='{next_month}   →')),
        Cancel(Const(text='☰ Главное меню')),
        getter=get_free_dates,
        state=UserNewAppointmentSG.calendary_first_month
    ),
    # отображение календаря с датами на следующий месяц
    Window(
        Const(text='Выберите дату для записи:'),
        Button(Format(text='{next_month}'), id='month'),
        Row(*get_weekday_button()),  # дни недели
        get_group(choose_date_for_appointment, 'date', 'next_month'),  # group, основная часть календаря
        Back(Format(text='←   {current_month}')),
        Cancel(Const(text='☰ Главное меню')),
        getter=get_free_dates,
        state=UserNewAppointmentSG.calendary_second_month,
    ),
    # отображение доступных временных "слотов" на выбранную дату
    # при нажатии на слот - происходит запись
    Window(
        Format(text='Доступное время для записи на {text_date}:'),
        get_group(choose_time_for_appointment, 'time'),  # group, отображение слотов
        SwitchTo(Const(text='← Назад'), id='b_back', state=UserNewAppointmentSG.calendary_first_month),
        getter=get_free_times_from_date,
        state=UserNewAppointmentSG.choose_time,
    ),
    # окно после успешной записи на выбранный "слот"
    Window(
        Format(text='Вы успешно записались на {date} - {time}!\n\n'
                    'Чтобы посмотреть список своих записей или отменить запись, выберите пункт "Мои записи" в главном меню.'),
        Cancel(Const(text='☰ Главное меню')),
        state=UserNewAppointmentSG.confirm_datetime,
        getter=get_confirm_datetime,
    ),
    # окно после неудачной записи на выбранный "слот"
    # (если "слот" закрыли или заняли в момент выбора)
    Window(
        Format(text='Произошла ошибка во время записи на {date} - {time}!\n'
                    'Возможно, выбранное время уже занято.\n'
                    'Пожалуйста, попробуйте еще раз или выберите другое время.'),
        Cancel(Const(text='☰ Главное меню')),
        state=UserNewAppointmentSG.error_confirm,
        getter=get_confirm_datetime,
    ),
    # окно при превышении лимита количества записей пользователя (по умолчанию - 2)
    Window(
        Const(
            text='Вы записаны максимальное количество раз.\nЧтобы изменить время записи, пожалуйста, отмените одну из Ваших записей.\n\n'
                 '(Мои записи -> отменить запись)'),
        Cancel(Const(text='☰ Главное меню')),
        state=UserNewAppointmentSG.user_max_appointment,
    ),
    # Окно для написания комментария при записи
    # (функционал администратора)
    Window(
        Format(text='Создание новой записи на {date} - {time}.\n\n'
                    'Пожалуйста, напишите комментарий для записи.\n'
                    'Он будет отображаться при просмотре записей \n'
                    'Важно: имя и телефон будут отображаться Ваши. Комментарий нужен чтобы Вы знали, кто записан на эту дату'),
        TextInput(
            id='input_comment',
            on_success=confirmed_admin_appointment,
        ),
        Button(Const(text='← Назад'), id='b_back', on_click=back_btn_adm_appointment),
        state=UserNewAppointmentSG.write_admin_comment,
        getter=get_confirm_datetime,
    ),
    # Окно подтверждения ручной записи
    # (функционал администратора)
    Window(
        Format(text='Подтверждение записи:\n'
                    'Дата: {date}\n'
                    'Время: {time}\n'
                    'Комментарий администратора: {comment}\n\n'),
        Button(Const('Подтвердить запись'), id='b_confirm', on_click=make_admin_comment),
        Back(Const(text='Назад')),
        state=UserNewAppointmentSG.admin_confirmed_new_appointment,
        getter=get_confirm_datetime,
    ),
    # Окно успешной ручной записи
    # (функционал администратора)
    Window(
        Format(text='Вы успешно создали запись {date} - {time}!\n'
                    'Комментарий: {comment}'),
        Cancel(Const(text='☰ Главное меню')),
        state=UserNewAppointmentSG.confirm_admin_datetime,
        getter=get_confirm_datetime,
    ),
)
