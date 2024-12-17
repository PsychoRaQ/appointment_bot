from src.db.models import Users, Slots
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

import logging

logger = logging.getLogger(__name__)

'''
Функции для работы с базой данных
через алхимию
Потом подключить логирование
'''


# Добавляем пользователя в базу данных
async def add_new_user(session: AsyncSession, user_id, username, phone):
    stmt = upsert(Users).values(
        {
            'telegram_id': user_id,
            'username': username,
            'phone': phone
        }
    )

    stmt = stmt.on_conflict_do_update(index_elements=['telegram_id'],
                                      set_=dict(username=username, phone=phone),
                                      )
    await session.execute(stmt)
    await session.commit()


# Получение пользователя из базы по его telegram_id
async def user_is_register(session: AsyncSession, user_id):
    result = await session.get(Users, user_id)
    return result


# Получение количества занятых слотов пользователем по его telegram_id
async def get_slot_with_user_id(session: AsyncSession, user_id):
    stmt = select(Slots).where(Slots.user_id == user_id).order_by(Slots.date, Slots.time)  # noqa
    result = await session.execute(stmt)
    return result.scalars().all()


# Получение свободных дат для записи пользователя
async def get_free_dates_from_db(session: AsyncSession):
    stmt = select(Slots).where(and_(Slots.is_locked == 0, Slots.user_id == 0)).order_by(Slots.date, Slots.time)
    result = await session.execute(stmt)
    return result.scalars()


# Получение свободных временных слотов на выбранную дату
async def get_free_time_on_date_from_db(date, session: AsyncSession):
    stmt = select(Slots).where(and_(Slots.date == date, Slots.user_id == 0, Slots.is_locked == 0)).order_by(Slots.time)
    result = await session.execute(stmt)
    return result.scalars()


# Изменение статуса слота со стороны пользователя (запись или отмена)
async def user_confirm_datetime(user_id, date, time, status, session: AsyncSession):
    stmt = select(Slots).where(and_(Slots.date == date, Slots.time == time))
    result = await session.execute(stmt)
    slot = result.scalar()
    match status:
        case 'confirm':
            if slot.user_id != 0:
                return False
            slot.user_id = user_id
            await session.commit()
            return True
        case 'delete':
            slot.user_id = 0
            await session.commit()
            return True
        case _:
            return False
