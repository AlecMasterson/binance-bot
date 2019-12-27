from sqlalchemy import Column, String, Float
from sqlalchemy.ext.declarative import declarative_base


class Balance(declarative_base()):
    __tablename__ = 'balance'

    user = Column(String(20), primary_key=True, nullable=False)
    asset = Column(String(10), primary_key=True, nullable=False)
    free = Column(Float, primary_key=False, nullable=False)
    locked = Column(Float, primary_key=False, nullable=False)
