from sqlalchemy import Column, DateTime, Float, Integer, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OAGoldenOpenAccess(Base):
    __tablename__ = "oa_golden_open_access"

    year = Column(Integer, primary_key=True)
    cern_read_and_publish = Column(Float)
    cern_individual_apcs = Column(Float)
    scoap3 = Column(Float)
    other = Column(Float)
    other_collective_models = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
