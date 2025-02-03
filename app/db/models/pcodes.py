from app.db import Base
from sqlalchemy import Column, BigInteger, String

'''
Модель таблицы для хранения промокодов
'''


class Pcodes(Base):
    __tablename__ = 'pcodes'

    admin_id = Column(BigInteger, primary_key=True)
    pcode = Column(String, default=None)
