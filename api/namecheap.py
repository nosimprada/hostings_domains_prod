import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Dict, Any

from aiohttp.client import ClientSession
from namecheapapi import DomainAPI
from xmltodict import parse

from utils.schemas.domain_db import DomainCreateResponse, DomainInfoResponse

executor = ThreadPoolExecutor(max_workers=10)


async def get_user_balance(api_user: str, api_key: str, api_username: str, api_client_ip: str) -> float | None:
    endpoint = f"""
        https://api.namecheap.com/xml.response?ApiUser={api_user}&ApiKey={api_key}
        &UserName={api_username}&Command=namecheap.users.getBalances&ClientIp={api_client_ip}
    """

    async with ClientSession() as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                xml_text = await response.text()
                data_dict = parse(xml_text)

                api_status = data_dict.get("ApiResponse", {}).get("@Status")
                if api_status != "OK":
                    error_msg = data_dict.get("ApiResponse", {}).get("Errors", {}).get("Error")
                    print(f"API Error: {error_msg}")
                    return None

                balance_result = data_dict["ApiResponse"]["CommandResponse"]["UserGetBalancesResult"]
                available_balance = balance_result.get("@AvailableBalance")

                if available_balance is not None:
                    return float(available_balance)
                else:
                    print(f"AvailableBalance not found in response")
                    return None
            print(f"HTTP Error {response.status}: {await response.text()}")
            return None


async def register_domain(api_user: str, api_key: str, api_username: str, api_client_ip: str,
                          data: Dict[str, Any]) -> DomainCreateResponse:
    api = DomainAPI(
        api_user=api_user,
        api_key=api_key,
        username=api_username,
        client_ip=api_client_ip,
        sandbox=False
    )

    domain = data.get("domain")
    years = data.get("years", 1)
    address = data.get("address", {})
    nameservers = data.get("nameservers", None)
    coupon = data.get("coupon", None)
    add_whoisguard = data.get("add_whoisguard", True)
    enable_whoisguard = data.get("enable_whoisguard", True)

    loop = asyncio.get_event_loop()
    registered = await loop.run_in_executor(
        executor,
        partial(
            api.register,
            domain=domain,
            years=years,
            address=address,
            nameservers=nameservers,
            coupon=coupon,
            add_whoisguard=add_whoisguard,
            enable_whoisguard=enable_whoisguard
        )
    )

    return DomainCreateResponse(id=registered["ID"], name=registered["Domain"])


async def set_dns_hosts(api_user: str, api_key: str, api_username: str, api_client_ip: str,
                        domain: str, ip_address: str) -> bool:
    domain_parts = domain.split('.')
    sld = domain_parts[0]
    tld = '.'.join(domain_parts[1:])

    params = {
        'ApiUser': api_user,
        'ApiKey': api_key,
        'UserName': api_username,
        'ClientIp': api_client_ip,
        'Command': 'namecheap.domains.dns.setHosts',
        'SLD': sld,
        'TLD': tld,
        'RecordType1': 'A',
        'HostName1': '@',
        'Address1': ip_address,
        'TTL1': '1800',
        'RecordType2': 'A',
        'HostName2': 'www',
        'Address2': ip_address,
        'TTL2': '1800'
    }

    async with ClientSession() as session:
        async with session.get("https://api.namecheap.com/xml.response", params=params) as response:
            if response.status == 200:
                xml_text = await response.text()
                result = parse(xml_text)

                if result["ApiResponse"]["@Status"] == "OK":
                    return True
                else:
                    print(f"Failed to set dns hosts: {result["ApiResponse"]["Errors"]["Error"]}")
                    return False
            else:
                print(f"HTTP error when settings dns hosts. Status: {response.status} Details: {await response.text()}")
                return False


async def get_domain_info(api_user: str, api_key: str, api_username: str, api_client_ip: str,
                          domain: str) -> DomainInfoResponse | None:
    endpoint = f"""
        https://api.namecheap.com/xml.response?ApiUser={api_user}&ApiKey={api_key}
        &UserName={api_username}&Command=namecheap.domains.getinfo&ClientIp={api_client_ip}&DomainName={domain}
    """

    async with ClientSession() as session:
        async with session.get(endpoint) as response:
            if response.status == 200:
                xml_text = await response.text()
                data_dict = parse(xml_text)

                api_status = data_dict.get("ApiResponse", {}).get("@Status")
                if api_status != "OK":
                    error_msg = data_dict.get("ApiResponse", {}).get("Errors", {}).get("Error")
                    print(f"API Error: {error_msg}")
                    return None

                domain_info = data_dict["ApiResponse"]["CommandResponse"]["DomainGetInfoResult"]

                return DomainInfoResponse(
                    id=domain_info.get("@ID"),
                    name=domain_info.get("@DomainName"),
                    status=domain_info.get("@Status")
                )
            print(f"Error: {response.status}. Error text: {await response.text()}")
            return None


# async def reactivate_domain(
#         api_user: str, api_key: str, api_username: str, api_client_ip: str,
#         domain: str, add_years: int = 1, coupon: str = None
# ) -> dict:
#     api = DomainAPI(
#         api_user=api_user,
#         api_key=api_key,
#         username=api_username,
#         client_ip=api_client_ip,
#         sandbox=False
#     )
#
#     add_years = 2 if add_years > 1 else add_years
#
#     loop = asyncio.get_event_loop()
#
#     reactivated = await loop.run_in_executor(
#         executor,
#         partial(api.reactivate, domain=domain, years=add_years, coupon=coupon)
#     )
#
#     return reactivated


async def check_available_zones(
        api_user: str, api_key: str, api_username: str, api_client_ip: str,
        sld: str
) -> list[str] | None:
    if not _is_sld_format_valid(sld):
        return None

    api = DomainAPI(
        api_user=api_user,
        api_key=api_key,
        username=api_username,
        client_ip=api_client_ip,
        sandbox=False
    )

    loop = asyncio.get_event_loop()
    tld_list = await loop.run_in_executor(executor, api.get_tld_list)

    registerable_zones: Dict[str, dict] = {}
    for tld, info in tld_list.items():
        if info.get("IsApiRegisterable"):
            registerable_zones[tld] = info

    zones_to_check = list(registerable_zones.keys())[:20]
    checked_zones = await loop.run_in_executor(
        executor,
        lambda: api.check([f"{sld}.{topld}" for topld in zones_to_check])
    )

    available_zones: list[str] = []
    for zone, is_available in checked_zones.items():
        if is_available:
            tld = zone.split('.')[-1]
            available_zones.append(tld)

    return available_zones


def _is_sld_format_valid(sld: str) -> bool:
    if not sld:
        return False

    sld = sld.lower().strip()

    if len(sld) < 1:
        return False

    if len(sld) > 63:
        return False

    if not re.match(r'^[a-z0-9]([a-z0-9\-]*[a-z0-9])?$', sld):
        return False

    if '--' in sld:
        return False

    # Не должен начинаться или заканчиваться цифрой
    if sld[0].isdigit() or sld[-1].isdigit():
        return False

    return True


async def check_domain(
    api_user: str, api_key: str, api_username: str, api_client_ip: str,
    domain: str
) -> bool:
    api = DomainAPI(
        api_user=api_user,
        api_key=api_key,
        username=api_username,
        client_ip=api_client_ip,
        sandbox=False
    )

    loop = asyncio.get_event_loop()
    
    checked = await loop.run_in_executor(
        executor,
        partial(api.check, domains=[domain])
    )
    
    if isinstance(checked, dict):
        return bool(checked.get(domain, False))
    
    return bool(checked)