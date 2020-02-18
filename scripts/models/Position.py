from sqlalchemy import Column, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base


class Position(declarative_base()):
    __tablename__ = 'position'

    user = Column(String(20), primary_key=True)
    symbol = Column(String(20), primary_key=True)
    active = Column(Boolean, nullable=False)
    buyTime = Column(DateTime, primary_key=True)
    buyPrice = Column(Float, nullable=False)
    sellTime = Column(DateTime)
    sellPrice = Column(Float)
    amount = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)

    def __init__(self, user, symbol, buyTime, buyPrice, amount):
        self.user = user
        self.symbol = symbol
        self.active = True
        self.buyTime = buyTime
        self.buyPrice = buyPrice
        self.amount = amount
        self.roi = 1.0

    def sell(self, sellTime, sellPrice):
        self.active = False
        self.sellTime = sellTime
        self.sellPrice = sellPrice
        self.update_roi(sellPrice)

    def update_roi(self, curPrice):
        self.roi = curPrice / self.buyPrice
