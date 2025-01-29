# аиограм
from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Cancel, SwitchTo, Radio
from aiogram_dialog.widgets.text import Const, Format
# импорт состояний
from app.fsm.admin_states import AdminEditCalendary
# импорт сервисных функций-билдеров
from app.utils.widget_builder_for_dialogs import get_weekday_button, get_group
# для радиокнопок
import operator
# геттеры
from app.dialogs.user_dialogs.make_new_appointment.getters import get_free_dates
from app.dialogs.admin_dialogs.edit_calendary.getters import get_free_times_from_date, slot_info_for_user
# хэндлеры
from app.dialogs.admin_dialogs.edit_calendary.handlers import (admin_choose_time_slot_for_edit, admin_close_slot,
                                                               admin_choose_date_for_edit)

'''
Диалог редактирования своего расписания(графика) администратором.
Админ может изменять доступные для записи "слоты"", ему сразу же визуально видны все изменения.
Если админ хочет сделать недоступным "слот" к которому привязан пользователь - пользователь получит уведомление
об отмене его записи на выбранный "слот".

Календари с датами генерируются автоматически в момент открытия нужного окна диалога.
- Для настройки доступен текущий месяц и следующий.
- Для настройки доступны все даты, однако пользователям отображаются только даты с "сегодняшнего" дня и далее.

Инлайн кнопки с временными "слотами" генерируется автоматически в момент открытия нужного окна диалога, а также
после каждого изменения.
Админ может сам выбрать промежуток между временными "слотами" (по умолчанию - 30 минут).
Временные "слоты" доступны только в диапазоне 06:00 - 00:00.

Временной "слот" добавляется в базу данных только после первого изменения его состояния админом.
'''

# Диалог настройки расписания администратора
edit_calendary_dialog = Dialog(
    # отображение календаря на текущий месяц
    Window(
        Const(text='Выберите дату для изменения расписания:'),
        Button(Format(text='{current_month}'), id='month'),
        Row(*get_weekday_button()),
        get_group(admin_choose_date_for_edit, 'date', 'current_month'),  # group, основная часть календаря
        Next(Format(text='{next_month}   →')),
        Cancel(Const(text='☰ Главное меню')),
        getter=get_free_dates,
        state=AdminEditCalendary.first_month
    ),
    # отображение календаря на следующий месяц
    Window(
        Const(text='Выберите дату для изменения расписания:'),
        Button(Format(text='{next_month}'), id='month', ),
        Row(*get_weekday_button()),
        get_group(admin_choose_date_for_edit, 'date', 'next_month'),  # group, основная часть календаря
        Back(Format(text='←   {current_month}')),
        Cancel(Const(text='☰ Главное меню')),
        getter=get_free_dates,
        state=AdminEditCalendary.second_month
    ),
    # окно выбора временных "слотов" для изменения их доступности
    Window(
        Format(text='Изменение временных слотов на {text_date}:'),
        get_group(admin_choose_time_slot_for_edit, 'time'),  # group, отображение слотов
        # радио кнопки для изменения временного промежутка между "слотами"
        Row(
            Radio(
                checked_text=Format('🔘 {item[0]}'),
                unchecked_text=Format('⚪️ {item[0]}'),
                id='radio_times',
                item_id_getter=operator.itemgetter(1),
                items="slot_times",
            ),
        ),
        SwitchTo(Const(text='← Назад'), id='b_back', state=AdminEditCalendary.first_month),
        Cancel(Const(text='☰ Главное меню')),
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
        Button(Const(text='Подтвердить'), id='b_confirm', on_click=admin_close_slot),
        SwitchTo(Const(text='← Назад'), id='b_back', state=AdminEditCalendary.first_month),
        getter=slot_info_for_user,
        state=AdminEditCalendary.user_on_date,
    ),
)
