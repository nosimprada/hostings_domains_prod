from typing import List
from urllib.parse import urlencode

from aiohttp.client import ClientSession

BASE_URL = "https://api.dynadot.com/api3.json?key="


# BASE_URL = "https://api-sandbox.dynadot.com/api3.json?key="


async def get_user_balance(api_key: str) -> float | None:
    """
        Example values for request
        :param api_key: "..."
        :return: user balance as float
    """

    endpoint = f"{BASE_URL}{api_key}&command=get_account_balance"

    async with ClientSession() as session:
        async with session.get(endpoint) as response:
            data = await response.json(content_type=None)
            print(await response.text())

            balance_response = data.get("GetAccountBalanceResponse", {})
            response_error = balance_response.get("Error")
            response_status = balance_response.get("Status")

            if not balance_response or response_status != "success":
                if response_error and response_error == "There is no balance in your account":
                    return 0

                print(f"Status is not success: {await response.text()}")
                return None

            balance_list = balance_response.get("BalanceList", [])
            for balance in balance_list:
                amount_str = balance.get("Amount")
                return float(amount_str) if amount_str else None

    return None


async def register_domain(api_key: str, domain: str, years: int, currency: str) -> str | None:
    """
        Example values for request
        :param api_key: "..."
        :param domain: "example.com"
        :param years: 1
        :param currency: "USD"
        :return: None
    """

    endpoint = f"{BASE_URL}{api_key}&command=register&domain={domain}&duration={years}&currency={currency}"

    async with ClientSession() as session:
        async with session.get(endpoint) as response:
            data = await response.json(content_type=None)

            register_response = data.get("RegisterResponse", {})
            response_status = register_response.get("Status")

            if not register_response or response_status != "success":
                print(f"Status is not success: {await response.text()}")
                return None

            return register_response.get("DomainName") if register_response else None
        
async def domain_available(api_key: str, domain: str) -> bool | None:
    """
        :param api_key: "..."
        :param domain: "example.com"
        :return: True if available, False if not, None if error
    """
    domain = domain.lower()
    endpoint = f"{BASE_URL}{api_key}&command=search&domain0={domain}"

    async with ClientSession() as session:
        async with session.get(endpoint) as response:
            data = await response.json(content_type=None)
            print(data)

            search_response = data.get("SearchResponse", {})
            search_results = search_response.get("SearchResults", [])
            if not search_results:
                print(f"Status is not success: {await response.text()}")
                return None

            # Берём первый результат (или ищем по имени)
            for result in search_results:
                if result.get("DomainName", "").lower() == domain:
                    available_str = result.get("Available", "").lower()
                    return available_str == "yes"
            # Если не нашли — None
            return None

    return None


async def set_dns_hosts(api_key: str, domains: List[str], ip_address: str) -> bool:
    """
        Example values for request
        :param api_key: "..."
        :param domains: ["example.com", "test.com", "demo.com"]
        :param ip_address: "192.168.1.1"
        :return: None
    """

    if len(domains) > 100:
        print("Error: Maximum 100 domains per request")
        return False

    request_data = {
        "domain": ",".join(domains),
        "main_record_type0": "a",
        "main_record_0": ip_address,
        "main_record_type1": "a",
        "main_record_1": ip_address,
        "main_recordx1": "www",
        "ttl": "1800"
    }

    endpoint = f"{BASE_URL}{api_key}&command=set_dns2&{urlencode(request_data)}"

    async with ClientSession() as session:
        async with session.get(endpoint, data=request_data) as response:
            data = await response.json(content_type=None)
            print(data)

            set_response = data.get("SetDnsResponse", {})
            if not set_response or set_response.get("Status") != "success":
                print(f"Status is not success: {await response.text()}")
                return False

    return True
