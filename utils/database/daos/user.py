from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models.user import User
from utils.schemas.user_db import (
    NamecheapDataReadSchema,
    UserRole, 
    UserCreateSchema, 
    UserReadSchema,
    NamecheapDataSchema
    )

class UserDAO:
    @staticmethod
    async def create(session: AsyncSession, user_data: UserCreateSchema) -> UserReadSchema:
        user = User(
            tg_id=user_data.tg_id,
            username=user_data.username,
            role=user_data.role,
            hestia_username=user_data.hestia_username,
            FTP_username=user_data.FTP_username,
            hestia_password=user_data.hestia_password,
            FTP_password=user_data.FTP_password
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserReadSchema.model_validate(user)
    
    @staticmethod
    async def get_by_tg_id(session: AsyncSession, tg_id: int) -> UserReadSchema | None:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()
        if user:
            return UserReadSchema.model_validate(user)
        return None
    
    @staticmethod
    async def update_role_worker(session: AsyncSession, tg_id: int) -> UserReadSchema | None:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()
        if user:
            user.role = UserRole.WORKER
            await session.commit()
            await session.refresh(user)
            return UserReadSchema.model_validate(user)
        return None

    @staticmethod
    async def block_user(session: AsyncSession, tg_id: int) -> UserReadSchema | None:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()
        if user:
            user.is_blocked = True
            await session.commit()
            await session.refresh(user)
            return UserReadSchema.model_validate(user)
        return None
    
    @staticmethod
    async def get_namecheap_credentials(session: AsyncSession, tg_id: int) -> NamecheapDataReadSchema | None:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()
        if user:
            return NamecheapDataReadSchema(
                user_id=user.tg_id,
                namecheap_enabled=user.namecheap_enabled,
                api_user=user.namecheap_api_user,
                api_key=user.namecheap_api_key
            )
        return None
    
    @staticmethod
    async def update_namecheap_credentials(session: AsyncSession, credentials: NamecheapDataSchema) -> NamecheapDataReadSchema | None:
        result = await session.execute(select(User).where(User.tg_id == credentials.user_id))
        user = result.scalars().first()
        if user:
            if credentials.api_user is not None:
                user.namecheap_api_user = credentials.api_user
            if credentials.api_key is not None:
                user.namecheap_api_key = credentials.api_key
            await session.commit()
            await session.refresh(user)
            return NamecheapDataReadSchema(
                user_id=user.tg_id,
                namecheap_enabled=user.namecheap_enabled,
                api_user=user.namecheap_api_user,
                api_key=user.namecheap_api_key
            )
        return None
    
    @staticmethod
    async def update_namecheap_enabled(session: AsyncSession, tg_id: int, enabled: bool) -> bool:
        result = await session.execute(
            update(User)
            .where(User.tg_id == tg_id)
            .values(namecheap_enabled=enabled)
            .execution_options(synchronize_session="fetch")
        )
        await session.commit()
        return result.rowcount > 0

    @staticmethod
    async def get_all_active_users(session: AsyncSession) -> list[UserReadSchema]:
        result = await session.execute(select(User).where(User.is_blocked == False))
        users = result.scalars().all()
        return [UserReadSchema.model_validate(user) for user in users]
    
    @staticmethod
    async def get_credentials_fro_namecheap(session: AsyncSession, tg_id: int) -> NamecheapDataSchema | None:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()
        if user and user.namecheap_enabled and user.namecheap_api_key and user.namecheap_api_user:
            return NamecheapDataSchema(
                api_user=user.namecheap_api_user,
                api_key=user.namecheap_api_key
            )
        return None