from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base


class Balance(declarative_base()):
    __tablename__ = 'balance'

    user = Column(String(20), primary_key=True)
    asset = Column(String(10), primary_key=True)
    free = Column(Float, nullable=False)
    locked = Column(Float, nullable=False)
