
import asyncio
from api.hestia import enable_ssl_for_domain
from utils.database.services.domain import get_domains_by_ssl_off, update_domain_ssl_activated
from utils.database.services.server import get_server_by_id
from utils.database.services.user import get_user_by_tg_id
from utils.schemas.server_db import ServerReadSchema


async def get_line(length: int = 30) -> str:
    return "=" * length

async def get_available_slots_by_server_id(server_id: str) -> int:
    from utils.database.services.server import get_server_by_id
    from utils.database.services.domain import get_active_domains_by_server_id
    server = await get_server_by_id(server_id)
    if not server:
        return 0
    active_domains = await get_active_domains_by_server_id(server_id)
    used_slots = len(active_domains)
    return max(0, server.max_domains - used_slots)

async def get_total_available_slots(user_id: int) -> int:
    from utils.database.services.server import get_active_servers_by_user_id
    servers = await get_active_servers_by_user_id(user_id)
    total_free_slots = 0
    for server in servers:
        free_slots = await get_available_slots_by_server_id(server.server_id)
        total_free_slots += free_slots
    return total_free_slots

    

async def get_available_server_ip_for_domain(user_id: int) -> str | None:
    from utils.database.services.server import get_active_servers_by_user_id
    from utils.database.services.domain import get_active_domains_by_server_id

    servers = await get_active_servers_by_user_id(user_id)
    if not servers:
        return None
    if len(servers) == 1:
        return servers[0].server_ip

    min_count = None
    selected_server_ip = None
    for server in servers:
        active_domains = await get_active_domains_by_server_id(server.server_id)
        count = len(active_domains)
        if min_count is None or count < min_count:
            min_count = count
            selected_server_ip = server.server_ip
            print(f"Selected server {server.server_ip} with {count} domains !!!!!!!!!!!!!!!!")

    return selected_server_ip

async def get_servers_with_free_slots(user_id: int) -> list[ServerReadSchema]:
    from utils.database.services.server import get_active_servers_by_user_id
    from utils.database.services.domain import get_active_domains_by_server_id

    servers = await get_active_servers_by_user_id(user_id)
    servers_with_slots = []
    for server in servers:
        active_domains = await get_active_domains_by_server_id(server.server_id)
        if server.max_domains > len(active_domains):
            servers_with_slots.append(server)
            print(f"Server {server.server_ip} has free slots: {server.max_domains - len(active_domains)}")
    return servers_with_slots


async def ssl_enable_with_retries(selected_server_ip, server_password, hestia_username, domain_name, created_domain_id):
    retry_intervals = [60, 120, 180, 240, 300, 360, 420, 600]
    max_retries = len(retry_intervals)
    attempt = 0
    timeout_per_attempt = 70  # например, 70 секунд на одну попытку

    while True:
        try:
            result_enable_ssl = await asyncio.wait_for(
                enable_ssl_for_domain(
                    ssh_ip=selected_server_ip,
                    ssh_password=server_password,
                    hestia_username=hestia_username,
                    domain=domain_name.lower()
                ),
                timeout=timeout_per_attempt
            )
        except asyncio.TimeoutError:
            print(f"Попытка {attempt + 1}: таймаут ({timeout_per_attempt} сек) для домена {domain_name} на сервере {selected_server_ip}")
            result_enable_ssl = False

        if result_enable_ssl:
            print('===============================================================')
            print(result_enable_ssl)
            print(f"SSL успешно включен для домена {domain_name} на сервере {selected_server_ip}")
            print("Обновление SSL в БД:", created_domain_id, True)
            result = await update_domain_ssl_activated(created_domain_id, True)
            print("Результат update_domain_ssl_activated:", result)
            break
        else:
            print(f"Попытка {attempt + 1} не удалась для домена {domain_name} на сервере {selected_server_ip}")
            if attempt < max_retries:
                await asyncio.sleep(retry_intervals[attempt])
            else:
                print(f"Все попытки исчерпаны для домена {domain_name} на сервере {selected_server_ip}. SSL не удалось включить.")
                await asyncio.sleep(900)  # 15 минут
            attempt += 1

async def ssl_enable_worker():
    while True:
        print("Запуск SSL-воркера...")
        # Получить все домены без SSL
        domains = await get_domains_by_ssl_off()
        for domain in domains:
            try:
                user_data = await get_user_by_tg_id(domain.user_id)
                server_data = await get_server_by_id(domain.server_id)
                result_enable_ssl = await asyncio.wait_for(
                    enable_ssl_for_domain(
                        ssh_ip=server_data.server_ip,
                        ssh_password=server_data.server_password,
                        hestia_username=user_data.hestia_username,
                        domain=domain.domain_name.lower()
                    ),
                    timeout=70
                )
                if result_enable_ssl:
                    print(f"SSL успешно включен для {domain.domain_name}")
                    await update_domain_ssl_activated(domain.domain_id, True)
                else:
                    print(f"Не удалось включить SSL для {domain.domain_name}")
            except Exception as e:
                print(f"Ошибка при включении SSL для {domain.domain_name}: {e}")
        # Ждать 15 минут до следующего запуска
        await asyncio.sleep(900)