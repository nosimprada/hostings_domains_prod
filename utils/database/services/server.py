import random

from api.vultr import (
    get_plan_info,
    get_region_name
)
from config import OS_ID_FOR_VULTR, PLAN_FOR_VULTR
from utils.database.daos.server import ServerDAO
from utils.database.database import AsyncSessionLocal
from utils.schemas.server_db import (
    ServerCreateBeforeBuyingSchema,
    ServerCreateSchema,
    ServerProvider,
    ServerReadSchema
)


async def choose_server_before_buying(server_provider: ServerProvider) -> ServerCreateBeforeBuyingSchema | None:
    if server_provider == ServerProvider.VULTR:
        plan_id = PLAN_FOR_VULTR
        os_id = OS_ID_FOR_VULTR
        server_data = await get_plan_info(plan_id)
        if server_data is None:
            print("Не удалось получить данные сервера для выбранного плана.")
            return None
        region_id = random.choice(server_data.location_ids)
        region_name = await get_region_name(region_id)

        return ServerCreateBeforeBuyingSchema(
            server_provider=ServerProvider.VULTR,
            plan_id=plan_id,
            cpu_vendor=server_data.cpu_vendor,
            vcpu_count=server_data.vcpu_count,
            ram=server_data.ram,
            disk=server_data.disk,
            disk_type=server_data.disk_type,
            disk_count=server_data.disk_count,
            bandwidth=server_data.bandwidth,
            monthly_cost=server_data.monthly_cost,
            hourly_cost=server_data.hourly_cost,
            type=server_data.type,
            location_id=region_id,
            os_id=os_id,
            region_name=region_name
        )


async def create_server(server_data: ServerCreateSchema) -> ServerReadSchema:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.create_server(session, server_data)


async def get_server_by_id(server_id: str) -> ServerReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.get_server_by_id(session, server_id)


async def get_server_by_ip(server_ip: str) -> ServerReadSchema | None:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.get_server_by_ip(session, server_ip)


async def get_active_servers_by_user_id(user_id: int) -> list[ServerReadSchema]:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.get_active_servers_by_user_id(session, user_id)


async def get_active_servers_without_created_at_by_user_id(user_id: int) -> list[ServerReadSchema]:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.get_active_servers_without_created_at_by_user_id(session, user_id)


async def update_server_hestia_installed_status(server_id: int, hestia_installed: bool) -> bool:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.update_server_hestia_installed_status(session, server_id, hestia_installed)


async def update_server_status(server_id: int, server_status) -> bool:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.update_server_status(session, server_id, server_status)


async def get_all_active_servers() -> list[ServerReadSchema]:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.get_all_active_servers(session)


async def get_all_servers() -> list[ServerReadSchema]:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.get_all_servers(session)


async def update_server_max_domains(server_id: int, max_domains: int) -> bool:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.update_server_max_domains(session, server_id, max_domains)


async def reassign_server_owner(server_id: str, new_user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        return await ServerDAO.update_server_user_id(session, server_id, new_user_id)
