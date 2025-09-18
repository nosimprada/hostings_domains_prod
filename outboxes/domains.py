import asyncio
from aiogram.types import Message, CallbackQuery

from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from api import dynadot
from api.dynadot import domain_available
from api.hestia import add_domain, enable_ssl_for_domain
from api.namecheap import (
    check_domain, 
    register_domain, 
    set_dns_hosts
)
from config import (
    CLIENT_IP,
    FIRST_NAME,
    LAST_NAME,
    ADDRESS1,
    CITY,
    STATE_PROVINCE,
    POSTAL_CODE,
    COUNTRY,
    PHONE,
    EMAIL_ADDRESS
)
from keyboards.domains_kb import (
    back_domains_kb,
    choose_domain_slot_distribution_kb,
    confirm_buy_domains_dynadot_kb,
    confirm_buy_domains_namecheap_kb,
    get_available_servers_for_domain_binding_kb, 
    get_domains_menu_kb,
    get_users_list_for_reassign_kb,
    manage_domain_kb
)
from outboxes.sundry import (
    get_available_server_ip_for_domain, 
    get_total_available_slots,
    ssl_enable_with_retries
)
from utils.database.services.domain import (
    create_domain,
    get_active_domains_by_server_id,
    get_active_domains_by_user_id,
    get_domain_available_id,
    get_domain_by_id,
    update_domain_server_id,
    update_domain_ssl_activated,
    update_domain_user_id
)
from utils.database.services.server import get_active_servers_by_user_id, get_server_by_id, get_server_by_ip
from utils.database.services.user import get_user_by_tg_id
from utils.schemas.domain_db import DomainCreateSchema, DomainProvider
from utils.schemas.user_db import UserRole

async def domains_menu(callback: CallbackQuery, page: int = 1):
    domains_data = await get_active_domains_by_user_id(callback.from_user.id)
    count_active_domains = len(domains_data)
    msg_info = f"""
==============================
🏧<b>Домены (Активные)</b>
<b>┗ Личные: {count_active_domains}</b>
==============================
<b>Выберите домен для управления, или создайте новый:</b>
"""
    await callback.message.answer(
        text=msg_info,
        reply_markup=await get_domains_menu_kb(callback.from_user.id, page)
    )


async def handle_domain_input_to_namecheap_func(message: Message, state: FSMContext):
    user_data = await get_user_by_tg_id(message.from_user.id)
    state_data = await state.get_data()
    domains = state_data.get("domains", [])

    result_domains = []
    available_domains = []
    for domain in domains:
        is_available = await check_domain(
            api_user=user_data.namecheap_api_user,
            api_key=user_data.namecheap_api_key,
            api_username=user_data.namecheap_api_user,
            api_client_ip=CLIENT_IP,
            domain=domain
        )
        mark = "✅" if is_available else "❌"
        result_domains.append(f"{domain} {mark}")
        if is_available:
            available_domains.append(domain)

    msg_info = f"""
==============================
<b>Результаты проверки доменов:</b>
("✅" - доступен, "❌" - недоступен)
==============================
{'\n'.join(result_domains)}
==============================
<b>Доступно для покупки: {len(available_domains)}</b>
"""
    await state.update_data(domains=available_domains)
    await message.answer(text=msg_info, reply_markup=await confirm_buy_domains_namecheap_kb(len(available_domains)))


async def handle_domain_input_to_dynadot_func(message: Message, state: FSMContext):
    user_data = await get_user_by_tg_id(message.from_user.id)
    state_data = await state.get_data()
    domains = state_data.get("domains", [])

    result_domains = []
    available_domains = []
    for domain in domains:
        is_available = await domain_available(
            api_key=user_data.dynadot_api_key,
            domain=domain
        )
        mark = "✅" if is_available else "❌"
        result_domains.append(f"{domain} {mark}")
        if is_available:
            available_domains.append(domain)

    msg_info = f"""
==============================
<b>Результаты проверки доменов:</b>
("✅" - доступен, "❌" - недоступен)
==============================
{'\n'.join(result_domains)}
==============================
<b>Доступно для покупки: {len(available_domains)}</b>
"""
    await state.update_data(domains=available_domains)
    await message.answer(text=msg_info, reply_markup=await confirm_buy_domains_dynadot_kb(len(available_domains)))


async def handle_confirm_buy_domains_func(callback: CallbackQuery, state: FSMContext, provider: DomainProvider):
    state_data = await state.get_data()
    user_data = await get_user_by_tg_id(callback.from_user.id)
    domains = state_data.get("domains", [])
    if not domains:
        await callback.message.answer(text="Нет доступных доменов для покупки.")
        return

    log = []
    created_domain_ids = []
    if provider == DomainProvider.NAMECHEAP:
        for domain in domains:
            try:
                response = await register_domain(
                    api_user=user_data.namecheap_api_user,
                    api_key=user_data.namecheap_api_key,
                    api_username=user_data.namecheap_api_user,
                    api_client_ip=CLIENT_IP,
                    data={
                        "domain": domain,
                        "years": 1,
                        "address": {
                            "FirstName": FIRST_NAME,
                            "LastName": LAST_NAME,
                            "Address1": ADDRESS1,
                            "City": CITY,
                            "StateProvince": STATE_PROVINCE,
                            "PostalCode": POSTAL_CODE,
                            "Country": COUNTRY,
                            "Phone": PHONE,
                            "EmailAddress": EMAIL_ADDRESS
                        },
                        "nameservers": None,
                        "coupon": None,
                        "add_whoisguard": True,
                        "enable_whoisguard": True
                    }
                )
                print(response)  # Debugging line to check the response
                if response is not None:
                    domain_id = response.id
                    domain_name = response.name
                    domain_data = DomainCreateSchema(
                        user_id=callback.from_user.id,                    
                        domain_name=domain_name,
                        domain_provider=DomainProvider.NAMECHEAP,
                        domain_id=domain_id,
                    )
                    crated_domain_in_db = await create_domain(domain_data)
                    domain_id = crated_domain_in_db.domain_id
                    created_domain_ids.append(domain_id)
                    log.append(f"✅ {domain} — успешно куплен")
                else:
                    log.append(f"❌ {domain} — ошибка регистрации (нет ответа)")
            except Exception as e:
                log.append(f"❌ {domain} — ошибка регистрации: {e}")

    elif provider == DomainProvider.DYNADOT:
        for domain in domains:
            try:
                response = await dynadot.register_domain(
                    api_key=user_data.dynadot_api_key,
                    domain=domain,
                    years=1,
                    currency="USD"
                )
                print(response)  # Debugging line to check the response
                if response is not None:
                    domain_id = await get_domain_available_id()
                    domain_name = response
                    domain_data = DomainCreateSchema(
                        user_id=callback.from_user.id,                    
                        domain_name=domain_name,
                        domain_provider=DomainProvider.DYNADOT,
                        domain_id=domain_id,  # Dynadot does not provide a domain ID in this example
                    )
                    crated_domain_in_db = await create_domain(domain_data)
                    domain_id = crated_domain_in_db.domain_id
                    created_domain_ids.append(domain_id)
                    log.append(f"✅ {domain} — успешно куплен")
                else:
                    log.append(f"❌ {domain} — ошибка регистрации (нет ответа)")
            except Exception as e:
                log.append(f"❌ {domain} — ошибка регистрации: {e}")

    # Сохраняем список id созданных доменов в состояние
    await state.update_data(created_domain_ids=created_domain_ids)
    count_crated = len(created_domain_ids)
    if count_crated == 0:
        msg = "Не удалось купить ни одного домена."

    msg = (
        "==============================\n"
        "<b>Результаты покупки доменов:</b>\n"
        "==============================\n"
        + "\n".join(log)
        + "\n==============================\n"
        "<b>Вы можете распределить домены по свободным слотам на серверах автоматически, или же сделать это позже вручную.</b>"
    )

    await callback.message.answer(text=msg, reply_markup=await choose_domain_slot_distribution_kb(len(created_domain_ids)))


async def auto_distribute_domains(user_id: int, created_domain_ids: list[str]):
    user_data = await get_user_by_tg_id(user_id)
    if not created_domain_ids:
        return "Нет доступных доменов для распределения."
    
    servers = await get_active_servers_by_user_id(user_id)
    if not servers:
        return "У вас нет активных серверов для распределения доменов."

    total_available_slots = await get_total_available_slots(user_id)
    if total_available_slots == 0:
        return "У вас нет доступных слотов на серверах для распределения доменов."

    log = []
    # Распределяем только столько доменов, сколько есть слотов
    for created_domain_id in created_domain_ids[:total_available_slots]:
        domain = await get_domain_by_id(created_domain_id)
        selected_server_ip = await get_available_server_ip_for_domain(user_id)
        print("Выбранный IP сервера:", selected_server_ip)  # Debugging line
        result_set_dns = False
        if domain.domain_provider == DomainProvider.NAMECHEAP:
            result_set_dns = await set_dns_hosts(
                api_user=user_data.namecheap_api_user,
                api_key=user_data.namecheap_api_key,
                api_username=user_data.namecheap_api_user,
                api_client_ip=CLIENT_IP,
                domain=domain.domain_name,
                ip_address=selected_server_ip
            )
        elif domain.domain_provider == DomainProvider.DYNADOT:
            result_set_dns = await dynadot.set_dns_hosts(
                api_key=user_data.dynadot_api_key,
                domains=[domain.domain_name],
                ip_address=selected_server_ip
            )

        if result_set_dns:
            server_data = await get_server_by_ip(selected_server_ip)
            result_add_domain = await add_domain(
                ssh_ip=selected_server_ip,
                ssh_password=server_data.server_password,
                hestia_username=user_data.hestia_username,
                domain=domain.domain_name
            )
            if result_add_domain:
                log.append(f"✅ {domain.domain_name} — успешно распределён на сервер {server_data.server_name} ({selected_server_ip})")
                update_domain_in_db = await update_domain_server_id(created_domain_id, server_data.server_id)
                print("Обновление домена в БД:", update_domain_in_db)  # Debugging line
                # asyncio.create_task(
                #     ssl_enable_with_retries(
                #         selected_server_ip,
                #         server_data.server_password,
                #         user_data.hestia_username,
                #         domain.domain_name,
                #         created_domain_id
                #     )
                # )
            else:
                log.append(f"❌ {domain.domain_name} — ошибка при добавлении на сервер {server_data.server_name} ({selected_server_ip})")
        else:
            log.append(f"❌ {domain.domain_name} — ошибка установки DNS")

    msg = (
        "==============================\n"
        "<b>Результаты автоматического распределения:</b>\n"
        "==============================\n"
        + "\n".join(log)
        + "\n=============================="
    )
    return msg

async def handle_action_auto_distribute_domains(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    created_domain_ids = state_data.get("created_domain_ids", [])
    if not created_domain_ids:
        await callback.message.answer("Нет доступных доменов для распределения.")
        return
    
    msg = await auto_distribute_domains(callback.from_user.id, created_domain_ids)
    await callback.message.answer(text=msg, reply_markup=await back_domains_kb())
                

        
async def get_domain_management_menu(callback: CallbackQuery, domain_id: str):
    domain = await get_domain_by_id(domain_id)
    # if not domain or domain.user_id != callback.from_user.id:
    #     await callback.message.answer("Домен не найден или у вас нет прав на его управление.")
    #     return

    server_data = await get_server_by_id(domain.server_id) if domain.server_id else None
    ssl_status = "🟢" if domain.ssl_activated else "⚠️"
    user_data = await get_user_by_tg_id(callback.from_user.id)
    owner_id = domain.user_id
    owner_data = await get_user_by_tg_id(owner_id)
    admin_header = f"<b>Владелец: @{owner_data.username}</b>" if user_data.role == UserRole.ADMIN and user_data.tg_id != owner_id else ""

    if server_data:
        server_info = f"<code>{server_data.server_ip}</code>"
        server_block = f"""
<b>🖥️ Сервер: {server_info}</b>
<b>🔒 SSL: {ssl_status}</b>
==============================
🌐 <b>SFTP/HestiaCP: 
📎 <a href="{server_data.hestia_url}">{server_data.hestia_url}</a></b>
┣ <b>Логин: <code>{owner_data.hestia_username}</code></b>
┗ <b>Пароль: <code>{owner_data.hestia_password}</code></b>
==============================
"""
    else:
        server_block = "<b>🖥️ Сервер: Не определён ⚠️</b>\n<b>🔒 SSL: {}</b>\n==============================".format(ssl_status)

    msg_info = f"""
{admin_header}
==============================
<b>🏷️ {domain.domain_name}</b>
==============================
{server_block}
"""
    await callback.message.answer(
        text=msg_info,
        reply_markup=await manage_domain_kb(domain_id, server_data, callback.from_user.id)
    )



async def handle_binding_domain_func(callback: CallbackQuery, domain_id: str):
    domain = await get_domain_by_id(domain_id)
    if not domain or domain.user_id != callback.from_user.id:
        await callback.message.answer("Домен не найден или у вас нет прав на его управление.")
        return

    if domain.server_id:
        await callback.message.answer("Домен уже привязан к серверу.")
        return

    msg_info = """
==============================
<b>Выберите сервер для привязки домена:</b>
==============================
"""
    await callback.message.answer(
        text=msg_info,
        reply_markup=await get_available_servers_for_domain_binding_kb(domain_id)
    )

async def confirm_bind_domain_func(callback: CallbackQuery, domain_id: str, server_id: int):
    domain = await get_domain_by_id(domain_id)
    if not domain or domain.user_id != callback.from_user.id:
        await callback.message.answer("Домен не найден или у вас нет прав на его управление.")
        return

    if domain.server_id:
        await callback.message.answer("Домен уже привязан к серверу.")
        return

    server_data = await get_server_by_id(server_id)
    if not server_data or server_data.user_id != callback.from_user.id:
        await callback.message.answer("Сервер не найден или у вас нет прав на его использование.")
        return

    user_data = await get_user_by_tg_id(callback.from_user.id)
    result_set_dns = False
    if domain.domain_provider == DomainProvider.NAMECHEAP:
        result_set_dns = await set_dns_hosts(
            api_user=user_data.namecheap_api_user,
            api_key=user_data.namecheap_api_key,
            api_username=user_data.namecheap_api_user,
            api_client_ip=CLIENT_IP,
            domain=domain.domain_name,
            ip_address=server_data.server_ip
        )
    elif domain.domain_provider == DomainProvider.DYNADOT:
        result_set_dns = await dynadot.set_dns_hosts(
            api_key=user_data.dynadot_api_key,
            domains=[domain.domain_name],
            ip_address=server_data.server_ip
        )

    if result_set_dns:
        result_add_domain = await add_domain(
            ssh_ip=server_data.server_ip,
            ssh_password=server_data.server_password,
            hestia_username=user_data.hestia_username,
            domain=domain.domain_name
        )
        if result_add_domain:
            update_domain_in_db = await update_domain_server_id(domain_id, server_data.server_id)
            print("Обновление домена в БД:", update_domain_in_db)  # Debugging line
            await callback.message.answer(f"✅ Домен {domain.domain_name} успешно привязан к серверу {server_data.server_name} ({server_data.server_ip}).", reply_markup=await back_domains_kb())
            # asyncio.create_task(
            #     ssl_enable_with_retries(
            #         server_data.server_ip,
            #         server_data.server_password,
            #         user_data.hestia_username,
            #         domain.domain_name,
            #         domain_id
            #     )
            # )
        else:
            await callback.message.answer(f"❌ Ошибка при добавлении домена {domain.domain_name} на сервер {server_data.server_name}.")
    else:
        await callback.message.answer(f"❌ Ошибка установки DNS для домена {domain.domain_name}.")


async def get_active_users_for_reassign_domain(callback: CallbackQuery, domain_id: int):
    domain = await get_domain_by_id(domain_id)
    if not domain:
        await callback.message.answer("Домен не найден.")
        return
    

    msg_info = f"""
==============================
<b>Выберите нового владельца для домена:</b>
<b>*{domain.domain_name}*</b>
==============================
"""
    await callback.message.answer(
        text=msg_info,
        reply_markup=await get_users_list_for_reassign_kb(domain.user_id, domain_id)
    )

async def reassign_domain_handler_func(callback: CallbackQuery, domain_id: int, new_user_id: int):
    domain = await get_domain_by_id(domain_id)
    if not domain:
        await callback.message.answer("Домен не найден.")
        return
    
    old_user_data = await get_user_by_tg_id(domain.user_id)
    new_user_data = await get_user_by_tg_id(new_user_id)
    if not new_user_data:
        await callback.message.answer("Новый владелец не найден.")
        return

    update_domain_in_db = await update_domain_user_id(domain_id, new_user_id)
    print("Обновление владельца домена в БД:", update_domain_in_db)  # Debugging line
    msg_info = f"""
==============================
<b>Домен {domain.domain_name} успешно передан от @{old_user_data.username} к @{new_user_data.username}.</b>
==============================
"""
    await callback.message.answer(text=msg_info)
    await get_domain_management_menu(callback, domain_id)
