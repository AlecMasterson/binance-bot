from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class Decision(declarative_base()):
    __tablename__ = 'decision'

    model = Column(String(20), primary_key=True)
    symbol = Column(String(20), primary_key=True)
    closeTime = Column(DateTime, primary_key=True)
    choice = Column(String(10), nullable=False)

    def __init__(self, model, symbol, closeTime, choice):
        self.model = model
        self.symbol = symbol
        self.closeTime = closeTime
        self.choice = choice
