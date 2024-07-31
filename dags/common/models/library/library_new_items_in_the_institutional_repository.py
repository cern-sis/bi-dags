from sqlalchemy import Column, DateTime, Float, Integer, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LibraryNewItemsInTheInstitutionalRepository(Base):
    __tablename__ = "library_items_in_the_institutional_repository"

    year = Column(Integer, primary_key=True)
    inspire_arxiv_records = Column(Float)
    inspire_curators_records = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
