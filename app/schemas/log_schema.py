from pydantic import BaseModel


class SecurityLogCreate(BaseModel):
    user_id: str
    event_type: str
    ip_address: str
    device: str
    location: str
    login_hour: int