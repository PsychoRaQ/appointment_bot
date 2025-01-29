# аиограм
from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Back, Next, Select, Group, Cancel
from aiogram_dialog.widgets.text import Const, Format, List
# состояния
from src.fsm.user_states import (UserAppointmentSG)
# геттеры
from src.dialogs.user_dialogs.user_appointments.getters import get_user_appointments
# хэндлеры
from src.dialogs.user_dialogs.user_appointments.handlers import (user_is_confirmed_delete_appointment,
                                                                 user_choose_slot_for_delete)

'''
Диалог просмотра (и отмены) записей пользователя.
Пользователю отображается список его записей в формате ДАТА - ВРЕМЯ.
Пользователь может отменить активную запись. Тогда временной "слот" будет считаться свободным и
доступным остальным пользователям. В метаданные отложенного сообщения вносятся изменения, и уведомление
за 24ч не будет приходить.

Диалог используется админами для функции "Отмены ручной записи", для этого добавлены дополнительные стейты.
'''

# пользователь выбрал "Мои записи" (+ отмена записей)
view_user_appointments_dialog = Dialog(
    # окно отображения пользователю всех его записей в виде списка
    Window(
        Const(text='Ваши записи:\n'),
        List(field=Format('{item[0]} - {item[1]}'),
             items='user_appointment'),
        Next(Const(text='Отменить запись')),
        Cancel(Const(text='← Назад')),
        state=UserAppointmentSG.main,
    ),
    # окно выбора записи пользователя для отмены
    # если администратор - дополнительно виден админ-комментарий к записи
    Window(
        Const(text='Выберите запись для отмены:'),
        Group(
            Select(
                Format('❌ {item[0]} - {item[1]}'), id='datetime',
                item_id_getter=lambda x: f'{x[0]}-{x[1]}',
                items='user_appointment',
                on_click=user_choose_slot_for_delete,
            ),
            width=1,
        ),
        Back(Const(text='← Назад'), when=~F['is_admin']),
        Cancel(Const(text='← Назад'), when=F['is_admin']),
        state=UserAppointmentSG.delete_appointment_datetime,
    ),
    # окно подтверждения отмены записи пользователя
    # если администратор - дополнительно виден админ-комментарий к записи
    Window(
        Format(text='Вы точно хотите отменить свою запись на {text_date} - {text_time} ?', when=~F['is_admin']),
        Format(text='Вы точно хотите отменить ручную запись на {text_date} - {text_time} ?\n'
                    'Комментарий: {comment}', when=F['is_admin']),
        Button(text=Const('Подтвердить отмену'), id='b_delete', on_click=user_is_confirmed_delete_appointment),
        Back(Const(text='← Назад')),
        state=UserAppointmentSG.delete_appointment_confirm,
    ),
    # окно успешной отмены записи
    Window(
        Format(text='Ваша запись на {text_date} - {text_time} была отменена.'),
        Cancel(Const(text='☰ Главное меню')),
        state=UserAppointmentSG.delete_appointment_result,
    ),
    # окно, если нет доступных записей
    # если администратор - меняется текст сообщения
    Window(
        Const(text='Записи не найдены.\nЧтобы записаться нажмите кнопку "Записаться" в главном меню бота.',
              when=~F['is_admin']),
        Const(
            text='Записи не найдены.\nЧтобы вручную записать человека, нажмите кнопку "Записать пользователя" в главном меню бота.',
            when=F['is_admin']),
        Cancel(Const(text='☰ Главное меню')),
        state=UserAppointmentSG.no_one_appointment,
    ),
    getter=get_user_appointments,
)
