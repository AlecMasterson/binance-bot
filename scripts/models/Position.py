from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base


class Position(declarative_base()):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True, nullable=False)
    user = Column(String(20), primary_key=False, nullable=False)
    symbol = Column(String(20), primary_key=False, nullable=False)
    active = Column(Boolean, primary_key=False, nullable=False)
    buyTime = Column(DateTime, primary_key=False, nullable=False)
    buyPrice = Column(Float, primary_key=False, nullable=False)
    sellTime = Column(DateTime, primary_key=False, nullable=True)
    sellPrice = Column(Float, primary_key=False, nullable=True)
    amount = Column(Float, primary_key=False, nullable=False)
    roi = Column(Float, primary_key=False, nullable=False)

    def sell(self, sellTime, sellPrice):
        self.sellTime = sellTime
        self.sellPrice = sellPrice
        self.roi = sellPrice / self.buyPrice
