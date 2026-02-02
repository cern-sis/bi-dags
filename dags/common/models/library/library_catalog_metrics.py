from sqlalchemy import Column, Date, DateTime, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class LibraryCatalogMetrics(Base):
    __tablename__ = "library_catalog_metrics"

    id = Column(Integer, autoincrement=True, primary_key=True)
    date = Column(Date, unique=False, nullable=False)
    category = Column(String, nullable=False)
    filter = Column(String, nullable=False, default="")
    aggregation = Column(String, nullable=False)
    key = Column(String, nullable=False)
    value = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    note = Column(String(length=255), nullable=True)
