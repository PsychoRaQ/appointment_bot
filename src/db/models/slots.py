from src.db import Base
from sqlalchemy import Column, BigInteger, String, Integer, Date, Time, ForeignKey


class Slots(Base):
    __tablename__ = 'slots'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    is_locked = Column(Integer, default=0)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id', ondelete='CASCADE'))
