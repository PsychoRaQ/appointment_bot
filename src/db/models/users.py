from src.db import Base
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, func


class Users(Base):
    __tablename__ = 'users'

    telegram_id = Column(BigInteger, primary_key=True)
    username = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    max_appointment = Column(Integer, default=2)
    is_admin = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
