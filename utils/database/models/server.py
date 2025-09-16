from datetime import (
    datetime, 
    timezone
    )
from sqlalchemy import (
    BigInteger,
    Column, 
    DateTime, 
    Integer, 
    String, 
    Boolean, 
    Enum, 
    ForeignKey
    )
from sqlalchemy.orm import relationship
from utils.schemas.server_db import (
    ServerProvider, 
    ServerStatus
)
from ..database import Base

class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    server_provider = Column(Enum(ServerProvider), default=ServerProvider.VULTR, nullable=False)
    server_id = Column(String, unique=True, nullable=False)
    server_ip = Column(String, unique=True, nullable=False)
    server_region = Column(String, nullable=False)
    server_name = Column(String, nullable=True)
    server_tag = Column(String, nullable=True)
    server_password = Column(String, nullable=True)
    server_status = Column(Enum(ServerStatus), default=ServerStatus.ACTIVE, nullable=False)

    hestia_installed = Column(Boolean, default=True, nullable=False)
    hestia_url = Column(String, nullable=True)
    FTP_installed = Column(Boolean, default=True, nullable=False)
    max_domains = Column(Integer, default=5, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", backref="servers")