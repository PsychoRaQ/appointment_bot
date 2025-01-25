# аиограм
import operator

from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Back, Next, Select, Group, Cancel, SwitchTo, Radio
from aiogram_dialog.widgets.text import Const, Format, List
# импорт состояний
from src.fsm.admin_states import (AdminMenuSG, AdminEditCalendary, AllAppointments, Dispatch, Pcode, AllAdmins,
                                  AdminSettings)
# импорт сервисных функций-билдеров
from src.services.widget_builder_for_dialogs import get_weekday_button, get_group
# импорт всех геттеров
from src.admin_dialogs.getters import (get_admin_menu, get_free_dates_on_next_month, get_free_dates_on_current_month,
                                       get_free_times_from_date, slot_info_for_user, get_all_slots, get_dispatch_text,
                                       get_pcode_from_db, get_pcode_from_dialog, get_admin_role, get_all_admins,
                                       get_admin_data, get_admin_feedback)
# хэндлеры для редактирования расписания
from src.admin_dialogs.handlers import admin_choose_date_for_edit, admin_choose_time_slot_for_edit, admin_close_slot
# хэндлеры для селектора (главное меню)
from src.admin_dialogs.handlers import admin_dialog_selection
# хэндлер для отображения всех записей
from src.admin_dialogs.handlers import admin_choose_date_for_look
# хэндлеры для рассылки
from src.admin_dialogs.handlers import edit_dispatch, start_dispatch
# хэндлеры для рефералок + промокодов
from src.admin_dialogs.handlers import check_pcode, edit_pcode, confirm_pcode
# различный функционал
from src.admin_dialogs.handlers import edit_admin_data, edit_sub_days, correct_id

'''
Все диалоги бота для администратора
(для функции ручной записи и удаления ручной записи используются пользовательские диалоги)
'''

# Главное меню
main_menu_dialog = Dialog(
    Window(
        Const(text='☰           Админка          ☰'),
        Group(
            Select(
                Format('{item[0]}'),
                id='main_menu',
                item_id_getter=lambda x: x[1],
                items='main_menu',
                on_click=admin_dialog_selection,
            ),
            width=1,
            when=F['user_role'] == 'admin' and F['subscribe'] == 'paid'
        ),
        Group(
            Select(
                Format('{item[0]}'),
                id='grand_admin_menu',
                item_id_getter=lambda x: x[1],
                items='grand_admin_menu',
                on_click=admin_dialog_selection,
            ),
            width=1,
            when=F['user_role'] == 'grand_admin'
        ),
        Next(Const(text='Продлить подписку'), id='pay_btn',
             when=F['user_role'] == 'admin' and F['subscribe'] == 'unpaid'),
        state=AdminMenuSG.admin_menu,
        getter=get_admin_menu
    ),
    Window(
        Format(text='Для продления подписки напишите администратору:'),
        Format(text='{url}'),
        Back(Const(text='← Назад'),
             id='b_button'),
        state=AdminMenuSG.unpaid_menu,
        getter=get_admin_feedback,
    ),
    getter=get_admin_role
)

# диалог настройки расписания
edit_calendary = Dialog(
    Window(
        Const(text='Выберите дату для изменения расписания:'),
        Button(Format(text='{current_month}'),
               id='month', ),
        Row(*get_weekday_button()),
        get_group(admin_choose_date_for_edit, 'date'),  # group, основная часть календаря
        Next(Format(text='{next_month}   →'),
             id='next_month_button'),
        Cancel(Const(text='☰ Главное меню'),
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
        Back(Format(text='←   {prev_month}'),
             id='prev_month_button'),
        Cancel(Const(text='☰ Главное меню'),
               id='cancel_button'),
        getter=get_free_dates_on_next_month,
        state=AdminEditCalendary.second_month,
    ),
    Window(
        Format(text='Изменение временных слотов на {text_date}:'),
        get_group(admin_choose_time_slot_for_edit, 'time'),  # group, отображение слотов
        Row(
            Radio(
                checked_text=Format('🔘 {item[0]}'),
                unchecked_text=Format('⚪️ {item[0]}'),
                id='radio_times',
                item_id_getter=operator.itemgetter(1),
                items="slot_times",
            ),
        ),
        SwitchTo(Const(text='← Назад'), id='b_button', state=AdminEditCalendary.first_month),
        Cancel(Const(text='☰ Главное меню'), id='cancel_button'),
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
        SwitchTo(Const(text='← Назад'), id='b_button', state=AdminEditCalendary.first_month),
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
        Next(Format(text='{next_month}   →'),
             id='next_month_button'),
        Cancel(Const(text='☰ Главное меню'),
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
        Back(Format(text='←   {prev_month}')),
        Cancel(Const(text='☰ Главное меню'),
               id='cancel_button'),
        getter=get_free_dates_on_next_month,
        state=AllAppointments.second_month
    ),
    Window(
        Format(text='Расписание {date}:\n'),
        List(field=Format('{item}'),
             items='slot'),
        SwitchTo(Const(text='← Назад'), id='b_button', state=AllAppointments.first_month),
        getter=get_all_slots,
        state=AllAppointments.appointments_list
    ),
)
# рассылка
dispatch_dialog = Dialog(
    Window(
        Const(text='Отправьте текст рассылки (форматирование будет сохранено):'),
        TextInput(
            id='input_dispatch',
            on_success=edit_dispatch
        ),
        Cancel(Const(text='☰ Главное меню'),
               id='cancel_button'),
        state=Dispatch.edit_dispatch
    ),
    Window(
        Const(text='Подтвердите рассылку:\n'),
        Format('{text}'),
        Button(Const(text='Запустить рассылку'), id='next_button', on_click=start_dispatch),
        Back(Const(text='← Назад'),
             id='b_button'),
        state=Dispatch.confirm_dispatch
    ),
    Window(
        Const(text='Рассылка отправлена!\n'
                   'Текст рассылки:\n'),
        Format('{text}'),
        Cancel(Const(text='☰ Главное меню'),
               id='cancel_button'),
        state=Dispatch.dispatch_is_successfull
    ),
    getter=get_dispatch_text
)

# рефералка + промокод
new_pcode = Dialog(
    Window(
        Format(text='Ваша реферальная ссылка: <code>{link}</code>\n'),
        Format(text='Ваш промокод: <code>{pcode}</code>\n'),
        Const(text='(нажмите чтобы скопировать)'),
        Next(Const(text='Изменить промокод'), id='next_button'),
        Cancel(Const(text='☰ Главное меню'),
               id='cancel_button'),
        state=Pcode.main_pcode,
        getter=get_pcode_from_db
    ),
    Window(
        Const(text='Отправьте новый промокод:\n'
                   '(2 - 10 символов, регистр не учитывается)'),
        TextInput(
            id='input_pcode',
            type_factory=check_pcode,
            on_success=edit_pcode
        ),
        Back(Const(text='← Назад'),
             id='b_button'),
        state=Pcode.edit_pcode,
        getter=get_pcode_from_dialog
    ),
    Window(
        Format(text='Подтвердите изменение промокода:\n'),
        Format(text='Новый промокод: {pcode}\n'),
        Button(Const(text='Подтвердить'), id='next_button', on_click=confirm_pcode),
        Back(Const(text='← Назад'),
             id='b_button'),
        state=Pcode.confirm_pcode,
        getter=get_pcode_from_dialog
    ),
    Window(
        Const(text='Промокод успешно изменен!\n'),
        Format(text='Новый промокод: {pcode}\n'),
        Cancel(Const(text='☰ Главное меню'),
               id='cancel_button'),
        state=Pcode.pcode_edit_successfull,
        getter=get_pcode_from_dialog
    ),
    Window(
        Const(text='Ошибка: не выполнены требования или такой промокод уже занят. '
                   'Пожалуйста, введите другой промокод\n'
                   '(2 - 10 символов, регистр не учитывается)'),
        TextInput(
            id='input_pcode',
            type_factory=check_pcode,
            on_success=edit_pcode
        ),
        Cancel(Const(text='☰ Главное меню'),
               id='cancel_button'),
        state=Pcode.error_pcode,
        getter=get_pcode_from_dialog
    ),
)

# список всех админов
all_admins = Dialog(
    Window(
        Format(text='Введите id администратора для управления.\n'
                    'Список админов: \n'),
        List(field=Format(
            '<b>{item[username]}</b>\nid - {item[admin_id]}\nТелефон - {item[phone]}\nПодписка - {item[sub_days]}\n'),
            items='admins'),
        TextInput(
            id='input_admin_id',
            type_factory=correct_id,
            on_success=edit_admin_data
        ),
        Cancel(Const(text='☰ Главное меню'),
               id='cancel_button'),
        getter=get_all_admins,
        state=AllAdmins.main_menu
    ),
    Window(
        Format(text='Администратор: <b>{admin_data[admin_id]}</b>'),
        Format(text='Дней подписки: <b>{admin_data[sub_days]}</b>'),
        Next(Const(text='Изменить время подписки'), id='next_button'),
        Back(Const(text='← Назад'),
             id='b_button'),
        getter=get_admin_data,
        state=AllAdmins.edit_admin_data
    ),
    Window(
        Format(text='Администратор: <b>{admin_data[admin_id]}</b>'),
        Format(text='Дней подписки: <b>{admin_data[sub_days]}</b>\n'
                    'Введите новое количество дней подписки.'),
        TextInput(
            id='input_sub_days',
            type_factory=correct_id,
            on_success=edit_sub_days
        ),
        Back(Const(text='← Назад'),
             id='b_button'),
        getter=get_admin_data,
        state=AllAdmins.edit_sub_days
    ),
)
# настройки админки
admin_settings = Dialog(
    Window(
        Format(text='Настройки админки:\n\n'
                    'Ваша подписка заканчивается через {admin_data[sub_days]} дней.'),
        Next(Const(text='Продлить подписку'), id='next_button'),
        Cancel(Const(text='☰ Главное меню'),
               id='cancel_button'),
        getter=get_admin_data,
        state=AdminSettings.main_menu
    ),
    Window(
        Format(text='Для продления подписки напишите администратору:'),
        Format(text='{url}'),
        Back(Const(text='← Назад'),
             id='b_button'),
        state=AdminSettings.feedback,
        getter=get_admin_feedback,
    ),
)
