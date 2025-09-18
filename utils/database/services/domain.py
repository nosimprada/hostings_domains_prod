from utils.database.daos.domain import DomainDAO
from utils.database.models.domain import Domain
from utils.schemas.domain_db import DomainCreateSchema, DomainReadSchema
from utils.database.database import AsyncSessionLocal

async def create_domain(domain_data: DomainCreateSchema) -> DomainReadSchema:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.create_domain(session, domain_data)

async def get_domain_by_id(domain_id: str) -> DomainReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.get_domain_by_id(session, domain_id)

async def get_active_domains_by_user_id(user_id: int) -> list[DomainReadSchema]:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.get_active_domains_by_user_id(session, user_id)

async def update_domain_status(domain_id: int, domain_status) -> bool:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.update_domain_status(session, domain_id, domain_status)

async def update_domain_ssl_activated(domain_id: int, ssl_activated: bool) -> bool:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.update_domain_ssl_activated(session, domain_id, ssl_activated)

async def get_active_domains_by_server_id(server_id: str) -> list[DomainReadSchema]:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.get_active_domains_by_server_id(session, server_id)

async def update_domain_server_id(domain_id: int, server_id: str) -> DomainReadSchema | None:
    print("Updating domain server ID")
    print(f"Domain ID: {domain_id}, Server ID: {server_id}")
    async with AsyncSessionLocal() as session:
        return await DomainDAO.update_domain_server_id(session, domain_id, server_id)
    
async def get_all_active_domains() -> list[DomainReadSchema]:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.get_all_active_domains(session)
    
async def update_domain_user_id(domain_id: int, new_user_id: int) -> DomainReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.update_domain_user_id(session, domain_id, new_user_id)
    
async def update_domains_user_ids_for_server(server_id: str, new_user_id: int) -> DomainReadSchema:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.update_domains_user_ids_for_server(session, server_id, new_user_id)
    
async def get_domain_available_id() -> int:
    async with AsyncSessionLocal() as session:
        return await DomainDAO.get_domain_available_id(session)
