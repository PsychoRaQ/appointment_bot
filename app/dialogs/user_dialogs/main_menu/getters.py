# Геттер для главного меню пользователя
async def get_main_menu(**kwargs) -> dict:
    main_menu = [
        ('🖊️ Записаться', 'make_new_appointment'),
        ('📖 Мои записи', 'view_my_appointments'),
        # ('💬 Обратная связь', 'user_feedback'),
    ]
    return {'main_menu': main_menu}
