from core.database import Base
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Unicode


class Diseases(Base):
    __tablename__ = "diseases"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(Unicode(200), nullable=False)
    group_name = Column(Unicode(100), nullable=False)
    risk_level = Column(String(20), nullable=False)
    icon = Column(Unicode(10), nullable=True)
    description = Column(Unicode(1000), nullable=False)
    symptoms = Column(Unicode(2000), nullable=True)
    causes = Column(Unicode(2000), nullable=True)
    diagnosis = Column(Unicode(2000), nullable=True)
    treatment = Column(Unicode(2000), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)