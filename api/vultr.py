import json
from typing import List, Dict, Any

from aiohttp.client import ClientSession

from config import VULTR_API_KEY
from utils.schemas.server_db import HostingInstanceSchema, NewServerSchema, ServerDataForPlanSchema

BASE_URL = "https://api.vultr.com/v2"

headers = {
    "Authorization": f"Bearer {VULTR_API_KEY}",
    "Content-Type": "application/json"
}


async def get_hostings_list() -> List[Dict[str, Any]]:
    endpoint = BASE_URL + "/instances"

    async with ClientSession(headers=headers) as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                return await response.json()
            return None


async def create_hosting(
        region: str, plan: str, os_id: int,
        user_data: str, label: str, tags: list[str] | None = None
) -> NewServerSchema:
    endpoint = BASE_URL + "/instances"

    request_data = {
        "region": region,
        "plan": plan,
        "os_id": os_id,
        "user_data": user_data,
        "tags": tags,
        "label": label
    }

    request_data = _remove_unfilled_fields(request_data)

    async with ClientSession(headers=headers) as session:
        async with session.post(endpoint, json=request_data) as response:
            if response.status == 202:
                data = await response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
                if data is None:
                    return None

                hosting = data.get("instance", {})

                return NewServerSchema(
                    server_id=hosting["id"],
                    server_ip=hosting["main_ip"],
                    server_region=hosting["region"],
                    server_name=hosting["label"],
                    server_tag=hosting["tag"],
                    server_password=hosting["default_password"],
                    hestia_url=f"https://{hosting["main_ip"]}:8083/"
                )
            return None


async def get_hosting(hosting_id: int) -> HostingInstanceSchema | None:
    endpoint = BASE_URL + f"/instances/{hosting_id}"

    async with ClientSession(headers=headers) as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                data = await response.json()
                instance = data.get("instance")
                if not instance:
                    return None

                # Преобразуем dict в объект схемы
                return HostingInstanceSchema(
                    server_id=instance["id"],
                    status=instance["status"],
                    power_status=instance["power_status"],
                    server_status=instance["server_status"],
                    main_ip=instance["main_ip"],
                    plan_id=instance["plan"],
                    vcpu_count=instance["vcpu_count"],
                    ram=instance["ram"],
                    os=instance["os"],
                )
            return None


async def update_hosting(
        hosting_id: int,
        app_id: int | None = None,
        image_id: int | None = None,
        backups: str | None = None,
        firewall_group_id: str | None = None,
        enable_ipv6: bool | None = None,
        os_id: int | None = None,
        user_data: str | None = None,
        tags: list[str] | None = None,
        plan: str | None = None,
        ddos_protection: bool | None = None,
        attach_vpc: list[str] | None = None,
        detach_vpc: list[str] | None = None,
        enable_vpc: bool | None = None,
        label: str | None = None,
        user_scheme: str | None = None
) -> List[Dict[str, Any]]:
    endpoint = BASE_URL + f"/instances/{hosting_id}"

    request_data = {
        "app_id": app_id,
        "image_id": image_id,
        "backups": backups,
        "firewall_group_id": firewall_group_id,
        "enable_ipv6": enable_ipv6,
        "os_id": os_id,
        "user_data": user_data,
        "tags": tags,
        "plan": plan,
        "ddos_protection": ddos_protection,
        "attach_vpc": attach_vpc,
        "detach_vpc": detach_vpc,
        "enable_vpc": enable_vpc,
        "label": label,
        "user_scheme": user_scheme,
    }

    request_data = _remove_unfilled_fields(request_data)

    async with ClientSession(headers=headers) as session:
        async with session.patch(endpoint, json=request_data) as response:
            if response.status == 202:
                return await response.json()
            return None


async def delete_hosting(hosting_id: int) -> None:
    endpoint = BASE_URL + f"/instances/{hosting_id}"

    async with ClientSession(headers=headers) as session:
        async with session.delete(endpoint):
            return None


async def get_region_name(region_id: str) -> str:
    endpoint = BASE_URL + "/regions"

    regions: Any = {}
    async with ClientSession(headers=headers) as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                data = await response.json()

                if data is not None:
                    regions = data.get("regions", {})

    for region in regions:
        if region["id"] == region_id:
            return region["city"]

    return None


async def get_regions() -> List[dict]:
    endpoint = BASE_URL + "/regions"

    async with ClientSession(headers=headers) as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                return await response.json()
            return None


async def get_plan_info(plan_id: str) -> ServerDataForPlanSchema:
    endpoint = BASE_URL + "/plans"

    plans: Any = {}
    async with ClientSession(headers=headers) as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                data = await response.json()
                if data is not None:
                    plans = data.get("plans", {})
            else:
                return None

    for plan in plans:
        if plan["id"] == plan_id:
            locations: list[str] = []
            for location in plan["locations"]:
                if await _is_region_in_europe(location):
                    locations.append(location)

            return ServerDataForPlanSchema(
                id=plan["id"],
                cpu_vendor=plan["cpu_vendor"],
                vcpu_count=plan["vcpu_count"],
                ram=plan["ram"],
                disk=plan["disk"],
                disk_type=plan["disk_type"],
                disk_count=plan["disk_count"],
                bandwidth=plan["bandwidth"],
                monthly_cost=plan["monthly_cost"],
                hourly_cost=plan["hourly_cost"],
                type=plan["type"],
                location_ids=locations
            )

    return None


async def get_plans() -> List[dict]:
    endpoint = BASE_URL + "/plans"

    async with ClientSession(headers=headers) as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                return await response.json()
            return None


async def get_os_ids() -> List[dict]:
    endpoint = BASE_URL + "/os"

    async with ClientSession(headers=headers) as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                return await response.json()
            return None


def _remove_unfilled_fields(data: dict) -> dict:
    return {key: value for key, value in data.items() if value is not None}


async def _get_region_info(region_id: str) -> dict:
    endpoint = BASE_URL + "/regions"

    regions: Any = {}
    async with ClientSession(headers=headers) as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                data = await response.json()
                if data is not None:
                    regions = data.get("regions", {})
                else:
                    return None
            else:
                return None

    for region in regions:
        if region["id"] == region_id:
            return region

    return None


async def _is_region_in_europe(region_id: str) -> bool:
    region = await _get_region_info(region_id)
    if region["continent"] == "Europe":
        return True

    return False
