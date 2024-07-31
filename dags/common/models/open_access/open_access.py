from sqlalchemy import Column, DateTime, Float, Integer, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OAOpenAccess(Base):
    __tablename__ = "oa_open_access"

    year = Column(Integer, primary_key=True)
    closed_access = Column(Float)
    bronze_open_access = Column(Float)
    green_open_access = Column(Float)
    gold_open_access = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
