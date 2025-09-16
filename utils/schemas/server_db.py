import enum
from typing import Optional
from xmlrpc.client import Boolean
from pydantic import BaseModel
from datetime import datetime

class ServerProvider(enum.Enum):
    VULTR = "Vultr"

class ServerStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    STOPED = "stopped"
    DELETED = "deleted"

class ServerDataForPlanSchema(BaseModel):
    id: str
    cpu_vendor: str
    vcpu_count: int
    ram: int
    disk: int
    disk_type: str
    disk_count: int
    bandwidth: int
    monthly_cost: float
    hourly_cost: float
    type: str
    location_ids: list[str]

    model_config = {"from_attributes": True}

class ServerCreateBeforeBuyingSchema(BaseModel):
    server_provider: ServerProvider
    plan_id: str
    cpu_vendor: str
    vcpu_count: int
    ram: int
    disk: int
    disk_type: str
    disk_count: int
    bandwidth: int
    monthly_cost: float
    hourly_cost: float
    type: str
    location_id: str
    os_id: int
    region_name: str

    model_config = {"from_attributes": True}

class NewServerSchema(BaseModel):
    server_id : str
    server_ip : str
    server_region : str
    server_name : str
    server_tag : str
    server_password : str
    hestia_url : str 

    model_config = {"from_attributes": True}

class ServerCreateSchema(BaseModel):
    user_id : int
    server_id : str
    server_ip : str
    server_region : str
    server_name : str
    server_tag : str
    server_password : str
    hestia_url : str 

    model_config = {"from_attributes": True}

class ServerReadSchema(BaseModel):
    id: int
    user_id: int
    server_id: str
    server_ip: str
    server_region: str
    server_name: str
    server_tag: str
    server_password: str
    hestia_url: str
    server_provider: ServerProvider
    server_status: ServerStatus
    hestia_installed: bool
    FTP_installed: bool
    max_domains: int
    created_at: datetime

    model_config = {"from_attributes": True}

class HostingInstanceSchema(BaseModel):
    server_id: str
    status: str
    power_status: str
    server_status: str
    main_ip: str
    plan_id: str
    vcpu_count: int
    ram: int
    os: str

    model_config = {"from_attributes": True}