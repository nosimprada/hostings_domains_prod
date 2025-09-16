from utils.database.daos.user import UserDAO
from utils.schemas.user_db import (
    NamecheapDataReadSchema,
    NamecheapDataSchema, 
    UserCreateSchema, 
    UserReadSchema
)
from utils.database.database import AsyncSessionLocal

async def create_user(user_data: UserCreateSchema) -> UserReadSchema:
    async with AsyncSessionLocal() as session:
        return await UserDAO.create(session, user_data)

async def get_user_by_tg_id(tg_id: int) -> UserReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.get_by_tg_id(session, tg_id)

async def block_user(tg_id: int) -> UserReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.block_user(session, tg_id)

async def update_user_role_worker(tg_id: int) -> UserReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.update_role_worker(session, tg_id)
    
async def get_namecheap_credentials(tg_id: int) -> NamecheapDataSchema | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.get_namecheap_credentials(session, tg_id)

async def get_all_active_users() -> list[UserReadSchema]:
    async with AsyncSessionLocal() as session:
        return await UserDAO.get_all_active_users(session)

async def get_namecheap_credentials(tg_id: int) -> NamecheapDataReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.get_namecheap_credentials(session, tg_id)

async def update_namecheap_credentials(credentials: NamecheapDataSchema) -> NamecheapDataReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await UserDAO.update_namecheap_credentials(session, credentials)
    
async def update_namecheap_enabled(tg_id: int, enabled: bool) -> bool:
    async with AsyncSessionLocal() as session:
        return await UserDAO.update_namecheap_enabled(session, tg_id, enabled)