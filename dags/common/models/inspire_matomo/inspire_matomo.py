from sqlalchemy import Column, Date, DateTime, Integer, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MatomoData(Base):
    __tablename__ = "inspire_matomo_data"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    visits = Column(Integer)
    unique_visitors = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
