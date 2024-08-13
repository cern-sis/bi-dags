from sqlalchemy import Column, DateTime, Float, Integer, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LibraryCernPublicationRecords(Base):
    __tablename__ = "library_cern_publication_records"

    year = Column(Integer, primary_key=True)
    publications_total_count = Column(Float)
    conference_proceedings_count = Column(Float)
    non_journal_proceedings_count = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
