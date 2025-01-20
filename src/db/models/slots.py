from src.db import Base
from sqlalchemy import Column, BigInteger, Integer, Date, Time, String

'''
Модель таблицы для хранения слотов
'''


class Slots(Base):
    __tablename__ = 'slots'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    is_locked = Column(Integer, default=0)
    user_id = Column(BigInteger, default=0)
    comment = Column(String, default=None)
    admin_id = Column(BigInteger, default=0)
