from datetime import (
    datetime, 
    timezone
    )
from sqlalchemy import (
    Column, 
    DateTime, 
    Integer, 
    String, 
    Boolean, 
    Enum, 
    BigInteger
    )
from  utils.schemas.user_db import UserRole
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    
    hestia_username = Column(String, default="admin", nullable=False)
    hestia_password = Column(String, nullable=True)
    
    FTP_username = Column(String, default="admin", nullable=False)
    FTP_password = Column(String, nullable=True)

    namecheap_enabled = Column(Boolean, default=False, nullable=False)
    namecheap_api_key = Column(String, nullable=True)
    namecheap_api_user = Column(String, nullable=True)

    dynadot_api_key = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    