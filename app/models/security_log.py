from sqlalchemy import Column, Integer, String, Float

from app.database.database import Base


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, nullable=False)

    event_type = Column(String, nullable=False)

    ip_address = Column(String)

    device = Column(String)

    location = Column(String)

    login_hour = Column(Integer)

    risk_score = Column(Float, default=0.0)

    status = Column(String, default="NORMAL")