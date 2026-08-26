from sqlalchemy import Column, Integer, String

from app.database.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, unique=True, nullable=False)

    role = Column(String)

    department = Column(String)

    normal_location = Column(String)

    normal_device = Column(String)