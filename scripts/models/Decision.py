from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


class Decision(declarative_base()):
    __tablename__ = 'decision'

    model = Column(String(20), primary_key=True, nullable=False)
    symbol = Column(String(20), primary_key=True, nullable=False)
    timestamp = Column(DateTime, primary_key=True, nullable=False)
    choice = Column(String(10), primary_key=False, nullable=False)

    def __init__(self, model, symbol, timestamp, choice):
        self.model = model
        self.symbol = symbol
        self.timestamp = timestamp
        self.choice = choice
