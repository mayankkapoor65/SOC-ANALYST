from sqlalchemy import Column, Integer, String, Float

from app.database.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=False)

    risk_score = Column(Float, nullable=False)

    alert_level = Column(String, nullable=False)

    reason = Column(String, nullable=False)