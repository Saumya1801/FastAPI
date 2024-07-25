from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class QueryLog(Base):
    __tablename__ = 'query_logs'
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(String, index=True)
    doctor_name = Column(String, index=True)
    area_of_expertise = Column(String, index=True)
    query = Column(Text, index=True)
    response = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    tokens_charged = Column(Integer)
    actual_cost = Column(Float)
