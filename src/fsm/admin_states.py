from aiogram.fsm.state import State, StatesGroup

'''
Состояния для всех диалогов (админка)
'''


# общее для админов

# Главное меню
class AdminMenuSG(StatesGroup):
    admin_menu = State()  # окно с главным меню бота (админка)


# Изменение расписания
class AdminEditCalendary(StatesGroup):
    first_month = State()  # календарь на текущий месяц
    second_month = State()  # календарь на следующий месяц
    choose_time = State()  # после выбора даты
    user_on_date = State()  # после выбора временного слота (если занят)


# Просмотр всех записей
class AllAppointments(StatesGroup):
    first_month = State()  # календарь на текущий месяц
    second_month = State()  # календарь на следующий месяц
    appointments_list = State()  # список открытых слотов на выбранную дату


# рассылка
class Dispatch(StatesGroup):
    edit_dispatch = State()  # ввод текста для рассылки
    confirm_dispatch = State()  # подтверждение данных рассылки
    dispatch_is_successfull = State()  # рассылка отправлена


# промокод
class Pcode(StatesGroup):
    main_pcode = State()  # отображение рефералки и промокода
    edit_pcode = State()  # изменение промокода
    confirm_pcode = State()  # подтверждение нового промокода
    pcode_edit_successfull = State()  # промокод успешно изменен
    error_pcode = State()  # ошибка в промокоде или он не уникальный


# старшая админка

# просмотр всех админов
class AllAdmins(StatesGroup):
    main_menu = State()  # список админов с дальнейшим управлением ими
    edit_admin_data = State()  # меню управления админами
    edit_sub_days = State()  # изменение дней подписки админа
