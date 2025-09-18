import random
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.database.models.domain import Domain
from utils.schemas.domain_db import (
    DomainCreateSchema, 
    DomainReadSchema,
    DomainStatus
)

class DomainDAO:
    @staticmethod
    async def create_domain(db: AsyncSession, domain: DomainCreateSchema) -> DomainReadSchema:
        new_domain = Domain(
            user_id=domain.user_id,
            domain_provider=domain.domain_provider,
            domain_id=domain.domain_id,
            domain_name=domain.domain_name,
        )
        db.add(new_domain)
        await db.commit()
        await db.refresh(new_domain)
        return DomainReadSchema.model_validate(new_domain)

    @staticmethod
    async def get_domain_by_id(db: AsyncSession, domain_id: str) -> DomainReadSchema | None:
        result = await db.execute(select(Domain).where(Domain.domain_id == domain_id))
        domain = result.scalars().first()
        if domain:
            return DomainReadSchema.model_validate(domain)
        return None

    @staticmethod
    async def get_active_domains_by_user_id(db: AsyncSession, user_id: int) -> list[DomainReadSchema]:
        result = await db.execute(select(Domain).where(Domain.user_id == user_id, Domain.domain_status == 'ACTIVE'))
        domains = result.scalars().all()
        return [DomainReadSchema.model_validate(domain) for domain in domains]

    @staticmethod
    async def update_domain_status(db: AsyncSession, domain_id: int, domain_status: DomainStatus) -> bool:
        result = await db.execute(
            update(Domain)
            .where(Domain.domain_id == domain_id)
            .values(domain_status=domain_status)
            .execution_options(synchronize_session="fetch")
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def update_domain_ssl_activated(db: AsyncSession, domain_id: int, ssl_activated: bool) -> bool:
        result = await db.execute(
            update(Domain)
            .where(Domain.domain_id == domain_id)
            .values(ssl_activated=ssl_activated)
            .execution_options(synchronize_session="fetch")
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def get_active_domains_by_server_id(db: AsyncSession, server_id: str) -> list[DomainReadSchema]:
        result = await db.execute(select(Domain).where(Domain.server_id == server_id, Domain.domain_status == 'ACTIVE'))
        domains = result.scalars().all()
        return [DomainReadSchema.model_validate(domain) for domain in domains]
    
    @staticmethod
    async def update_domain_server_id(db: AsyncSession, domain_id: int, server_id: str) -> DomainReadSchema | None:
        result = await db.execute(
            update(Domain)
            .where(Domain.domain_id == domain_id)
            .values(server_id=server_id)
            .execution_options(synchronize_session="fetch")
            .returning(Domain)
        )
        await db.commit()
        updated_domain = result.scalars().first()
        if updated_domain:
            return DomainReadSchema.model_validate(updated_domain)
        return None
    
    @staticmethod
    async def get_all_active_domains(db: AsyncSession) -> list[DomainReadSchema]:
        result = await db.execute(select(Domain).where(Domain.domain_status == 'ACTIVE'))
        domains = result.scalars().all()
        return [DomainReadSchema.model_validate(domain) for domain in domains]
    
    @staticmethod
    async def update_domain_user_id(db: AsyncSession, domain_id: int, new_user_id: int) -> DomainReadSchema | None:
        result = await db.execute(
            update(Domain)
            .where(Domain.domain_id == domain_id)
            .values(user_id=new_user_id)
            .execution_options(synchronize_session="fetch")
            .returning(Domain)
        )
        await db.commit()
        updated_domain = result.scalars().first()
        if updated_domain:
            return DomainReadSchema.model_validate(updated_domain)
        return None
    
    @staticmethod
    async def update_domains_user_ids_for_server(db: AsyncSession, server_id: str, new_user_id: int) -> DomainReadSchema:
        result = await db.execute(
            update(Domain)
            .where(Domain.server_id == server_id)
            .values(user_id=new_user_id)
            .execution_options(synchronize_session="fetch")
            .returning(Domain)
        )
        await db.commit()
        updated_domains = result.scalars().all()
        return [DomainReadSchema.model_validate(domain) for domain in updated_domains]

    @staticmethod
    async def get_domain_available_id(db: AsyncSession) -> int:
        while True:
            new_id = random.randint(10_000_000, 99_999_999)
            result = await db.execute(select(Domain).where(Domain.domain_id == new_id))
            domain = result.scalars().first()
            if not domain:
                return new_id
            
    @staticmethod
    async def get_domains_by_ssl_off(db: AsyncSession) -> list[DomainReadSchema]:
        result = await db.execute(select(Domain).where(Domain.ssl_activated == False, Domain.domain_status == 'ACTIVE'))
        domains = result.scalars().all()
        return [DomainReadSchema.model_validate(domain) for domain in domains]