from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base


class Symbol(declarative_base()):
    __tablename__ = 'symbol'

    name = Column(String(20), primary_key=True)
    active = Column(Boolean, nullable=False)
