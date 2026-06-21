from core.database import Base
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Unicode


class Drugs(Base):
    __tablename__ = "drugs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    code = Column(String(20), nullable=False)
    name = Column(Unicode(200), nullable=False)
    group_name = Column(Unicode(100), nullable=False)
    manufacturer = Column(Unicode(200), nullable=False)
    status = Column(String(20), nullable=False)
    rating = Column(Float, nullable=True)
    price = Column(Unicode(50), nullable=True)
    component = Column(Unicode(500), nullable=True)
    usage_info = Column(Unicode(1000), nullable=True)
    dosage = Column(Unicode(500), nullable=True)
    side_effects = Column(Unicode(1000), nullable=True)
    contraindications = Column(Unicode(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)