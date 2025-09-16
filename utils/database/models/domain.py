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
from utils.schemas.domain_db import (
    DomainProvider,
    DomainStatus
)
from ..database import Base

class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    server_id = Column(String, ForeignKey("servers.server_id"), nullable=True)
    domain_provider = Column(Enum(DomainProvider), default=DomainProvider.NAMECHEAP, nullable=False)
    domain_id = Column(String, unique=True, nullable=False)
    domain_name = Column(String, nullable=False)
    domain_status = Column(Enum(DomainStatus), default=DomainStatus.ACTIVE, nullable=False)
    ssl_activated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", backref="domains")
    server = relationship("Server", backref="domains")