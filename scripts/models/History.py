from sqlalchemy import Column, String, DateTime, Float, Integer
from sqlalchemy.ext.declarative import declarative_base


class History(declarative_base()):
    __tablename__ = 'history'

    symbol = Column(String(20), primary_key=True, nullable=False)
    width = Column(String(10), primary_key=True, nullable=False)
    open_time = Column(DateTime, primary_key=True, nullable=False)
    open = Column(Float, primary_key=False, nullable=False)
    high = Column(Float, primary_key=False, nullable=False)
    low = Column(Float, primary_key=False, nullable=False)
    close = Column(Float, primary_key=False, nullable=False)
    number_trades = Column(Integer, primary_key=False, nullable=False)
    volume = Column(Float, primary_key=False, nullable=False)
    close_time = Column(DateTime, primary_key=False, nullable=False)
