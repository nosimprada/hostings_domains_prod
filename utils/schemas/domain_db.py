import enum
from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class DomainProvider(enum.Enum):
    NAMECHEAP = "Namecheap"
    DYNADOT = "Dynadot"


class DomainStatus(enum.Enum):
    ACTIVE = "active"
    DELETED = "deleted"


class DomainCreateSchema(BaseModel):
    user_id: int
    domain_name: str
    domain_provider: DomainProvider
    domain_id: int

    model_config = {"from_attributes": True}


class DomainReadSchema(BaseModel):
    domain_id: int
    id: int
    user_id: int
    domain_name: str
    domain_provider: DomainProvider
    domain_status: DomainStatus
    server_id: Optional[str] = None
    ssl_activated: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DomainCreateResponse(BaseModel):
    id: int
    name: str


class DomainInfoResponse(BaseModel):
    id: int
    name: str
    status: str
