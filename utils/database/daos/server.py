from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from utils.database.models.server import Server
from utils.schemas.server_db import (
    ServerStatus,
    ServerCreateSchema,
    ServerReadSchema
)


class ServerDAO:
    @staticmethod
    async def create_server(db: AsyncSession, server: ServerCreateSchema) -> ServerReadSchema:
        new_server = Server(
            user_id=server.user_id,
            server_id=server.server_id,
            server_ip=server.server_ip,
            server_region=server.server_region,
            server_name=server.server_name,
            server_tag=server.server_tag,
            server_password=server.server_password,
            hestia_url=server.hestia_url,
        )
        db.add(new_server)
        await db.commit()
        await db.refresh(new_server)
        return ServerReadSchema.model_validate(new_server)

    @staticmethod
    async def get_server_by_id(db: AsyncSession, server_id: str) -> ServerReadSchema | None:
        result = await db.execute(select(Server).where(Server.server_id == server_id))
        server = result.scalars().first()
        if server:
            return ServerReadSchema.model_validate(server)
        return None

    @staticmethod
    async def get_server_by_ip(db: AsyncSession, server_ip: str) -> ServerReadSchema | None:
        result = await db.execute(select(Server).where(Server.server_ip == server_ip))
        server = result.scalars().first()
        if server:
            return ServerReadSchema.model_validate(server)
        return None

    @staticmethod
    async def get_active_servers_by_user_id(db: AsyncSession, user_id: int) -> list[ServerReadSchema]:
        min_created_at = datetime.now(timezone.utc) - timedelta(minutes=15)
        result = await db.execute(
            select(Server).where(
                and_(
                    Server.user_id == user_id,
                    Server.server_status == ServerStatus.ACTIVE,
                    Server.created_at <= min_created_at
                )
            )
        )
        servers = result.scalars().all()
        return [ServerReadSchema.model_validate(server) for server in servers]

    @staticmethod
    async def get_active_servers_without_created_at_by_user_id(db: AsyncSession, user_id: int) -> list[
        ServerReadSchema]:
        result = await db.execute(
            select(Server).where(
                and_(
                    Server.user_id == user_id,
                    Server.server_status == ServerStatus.ACTIVE
                )
            )
        )
        servers = result.scalars().all()
        return [ServerReadSchema.model_validate(server) for server in servers]

    @staticmethod
    async def update_server_hestia_installed_status(db: AsyncSession, server_id: int, hestia_installed: bool) -> bool:
        result = await db.execute(
            update(Server)
            .where(Server.id == server_id)
            .values(hestia_installed=hestia_installed)
            .execution_options(synchronize_session="fetch")
        )
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def update_server_status(db: AsyncSession, server_id: int, server_status: ServerStatus) -> bool:
        result = await db.execute(
            update(Server)
            .where(Server.server_id == server_id)
            .values(server_status=server_status)
            .execution_options(synchronize_session="fetch")
        )
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def get_all_active_servers(db: AsyncSession) -> list[ServerReadSchema]:
        result = await db.execute(select(Server).where(Server.server_status == ServerStatus.ACTIVE))
        servers = result.scalars().all()
        return [ServerReadSchema.model_validate(server) for server in servers]

    @staticmethod
    async def get_all_servers(db: AsyncSession) -> list[ServerReadSchema]:
        result = await db.execute(select(Server))
        servers = result.scalars().all()
        return [ServerReadSchema.model_validate(server) for server in servers]

    @staticmethod
    async def update_server_max_domains(db: AsyncSession, server_id: int, max_domains: int) -> bool:
        result = await db.execute(
            update(Server)
            .where(Server.id == server_id)
            .values(max_domains=max_domains)
            .execution_options(synchronize_session="fetch")
        )
        await db.commit()
        return result.rowcount > 0

    @staticmethod
    async def update_server_user_id(db: AsyncSession, server_id: str, new_user_id: int) -> ServerReadSchema | None:
        result = await db.execute(
            update(Server)
            .where(Server.server_id == server_id)
            .values(user_id=new_user_id)
            .execution_options(synchronize_session="fetch")
            .returning(Server)
        )
        await db.commit()
        updated_server = result.scalars().first()
        if updated_server:
            return ServerReadSchema.model_validate(updated_server)
        return None
