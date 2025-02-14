from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LibraryPeopleCounter(Base):
    __tablename__ = "library_people_counter"

    id = Column(Integer, autoincrement=True, primary_key=True)
    date = Column(DateTime, unique=True, nullable=False)
    occupancy = Column(Integer, nullable=False)
    people_in = Column(Integer, nullable=False)
    people_out = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
