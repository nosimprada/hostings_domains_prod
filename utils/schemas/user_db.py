import enum
from pydantic import BaseModel
from datetime import datetime

class UserRole(enum.Enum):
    USER = "USER"
    WORKER = "WORKER"
    ADMIN = "ADMIN"


class UserCreateSchema(BaseModel):
    tg_id: int
    username: str | None = None
    role: UserRole = UserRole.USER
    hestia_username: str 
    hestia_password: str 
    FTP_username: str 
    FTP_password: str

class UserReadSchema(BaseModel):
    id: int
    tg_id: int
    username: str | None = None
    role: UserRole
    is_blocked: bool

    hestia_username: str
    hestia_password: str | None = None

    FTP_username: str
    FTP_password: str | None = None

    namecheap_enabled: bool
    namecheap_api_key: str | None = None
    namecheap_api_user: str | None = None
    namecheap_username: str | None = None
    dynadot_api_key: str | None = None
    created_at: datetime
    class Config:
        from_attributes = True 

class NamecheapDataSchema(BaseModel):
    user_id: int
    api_user: str | None = None
    api_key: str | None = None

class NamecheapDataReadSchema(BaseModel):
    user_id: int
    namecheap_enabled: bool
    api_user: str | None = None
    api_key: str | None = None

class NamecheapDataForApiSchema(BaseModel):
    api_user: str | None = None
    api_key: str | None = None
    username: str | None = None
    client_ip: str | None = None

class DynadotDataSchema(BaseModel):
    user_id: int
    dynadot_api_key: str | None = None

class DynadotDataReadSchema(BaseModel):
    user_id: int
    dynadot_api_key: str | None = None