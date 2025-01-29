from app.db import Base
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, func

'''
Модель таблицы с пользователями
'''


class Users(Base):
    __tablename__ = 'users'

    telegram_id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    max_appointment = Column(Integer, default=2)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    admin_id = Column(BigInteger, default=0)
    role = Column(String, default='user')
