from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LibraryPeopleCounter(Base):
    __tablename__ = "library_people_counter"

    id = Column(Integer, autoincrement=True)
    date = Column(DateTime, primary_key=True)
    occupancy = Column(Integer)
    created_at = Column(DateTime, default=func.now())
