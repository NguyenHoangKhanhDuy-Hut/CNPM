from core.database import Base
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Unicode


class Prediction_histories(Base):
    __tablename__ = "prediction_histories"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(String(255), nullable=False)
    symptoms_input = Column(Unicode(2000), nullable=False)
    predicted_disease_id = Column(Integer, nullable=False)
    accuracy_score = Column(Integer, nullable=False)
    status = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)