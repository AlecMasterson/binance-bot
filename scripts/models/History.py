from sqlalchemy import Column, String, DateTime, Float, Integer
from sqlalchemy.ext.declarative import declarative_base


class History(declarative_base()):
    __tablename__ = 'history'

    symbol = Column(String(20), primary_key=True)
    width = Column(String(10), primary_key=True)
    openTime = Column(DateTime, primary_key=True)
    openPrice = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    closePrice = Column(Float, nullable=False)
    numberTrades = Column(Integer, nullable=False)
    volume = Column(Float, nullable=False)
    closeTime = Column(DateTime, nullable=False)

    def __init__(self, dictionary):
        for key in dictionary:
            setattr(self, key, dictionary[key])
