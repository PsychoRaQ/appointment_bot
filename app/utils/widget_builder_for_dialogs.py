# аиограм
from aiogram_dialog.widgets.kbd import Group, Select, Button
from aiogram_dialog.widgets.text import Format, Const

'''
Функции-билдеры для построения виджетов
'''


# Возвращает список с кнопками для отображения дней недели в календарях
def get_weekday_button():
    return [
        Button(Const(text='Пн'), id=''),
        Button(Const(text='Вт'), id=''),
        Button(Const(text='Ср'), id=''),
        Button(Const(text='Чт'), id=''),
        Button(Const(text='Пт'), id=''),
        Button(Const(text='Сб'), id=''),
        Button(Const(text='Вс'), id=''),
    ]


# Возвращает Group для отображения календаря / слотов
def get_group(on_click, datetime, month='current_month'):
    if datetime == 'date':
        id = 'date'
        getter = lambda x: x[1]
        items = 'current_month_dates' if month == 'current_month' else 'next_month_dates'
        width = 7
    elif datetime == 'time':
        id = 'time'
        getter = lambda x: x[0]
        items = 'open_time'
        width = 4
    return Group(
        Select(
            Format('{item[0]}'),
            id=id,
            item_id_getter=getter,
            items=items,
            on_click=on_click,
        ),
        width=width
    )
