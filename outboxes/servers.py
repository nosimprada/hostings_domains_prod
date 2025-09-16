import asyncio
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery
)

from api.hestia import change_user_password
from api.vultr import create_hosting, delete_hosting, get_hosting
from config import BOT_TOKEN, EMAIL
from keyboards.servers_kb import (
    get_confirm_delete_server_kb,
    get_info_servers_menu_kb,
    get_list_providers_kb,
    get_server_menu_kb,
    get_users_list_for_reassign_kb,
    select_buy_server_kb
)
from utils.database.services.domain import (
    get_active_domains_by_server_id,
    update_domain_status,
    update_domains_user_ids_for_server
)
from utils.database.services.server import (
    choose_server_before_buying,
    create_server,
    get_active_servers_by_user_id,
    get_all_active_servers,
    get_all_servers,
    get_server_by_id,
    reassign_server_owner,
    update_server_status
)
from utils.database.services.user import get_user_by_tg_id
from utils.encode_script import encode_hestia_script
from utils.schemas.domain_db import DomainStatus
from utils.schemas.server_db import ServerCreateSchema, ServerProvider, ServerStatus
from utils.schemas.user_db import UserRole


async def get_info_servers_menu(user_id: int) -> str:
    user_data = await get_user_by_tg_id(user_id)

    msg: str = ""

    if user_data.role == UserRole.ADMIN:
        servers = await get_active_servers_by_user_id(user_id)
        count_active_servers = len(servers)
        all_servers = await get_all_active_servers()
        count_all_active_servers = len(all_servers)
        msg = f"""
==============================
🌐<b>Серверы (Активные)</b>
<b>┣ Все: {count_all_active_servers}</b>
<b>┗ Личные: {count_active_servers}</b>
==============================
<b>Выберите сервер для управления, или создайте новый:</b>

"""
    elif user_data.role == UserRole.WORKER:
        servers = await get_active_servers_by_user_id(user_id)
        count_active_servers = len(servers)
        msg = f"""
==============================
🌐<b>Серверы (Активные)</b>
<b>┗ Личные: {count_active_servers}</b>
==============================
<b>Выберите сервер для управления, или создайте новый:</b>
"""
    return msg


async def send_servers_menu(callback: CallbackQuery):
    await callback.message.answer(
        text=await get_info_servers_menu(callback.from_user.id),
        reply_markup=await get_info_servers_menu_kb(callback.from_user.id)
    )


async def get_providers_list(message: Message):
    user_data = await get_user_by_tg_id(message.from_user.id)
    if user_data.role == UserRole.ADMIN or user_data.role == UserRole.WORKER:
        await message.answer(
            text="""
🌐 <b>Доступные провайдеры</b> 🌐
==============================
""",
            reply_markup=await get_list_providers_kb()
        )


async def get_choose_server_before_buying(callback: CallbackQuery, server_provider: ServerProvider,
                                          state: FSMContext) -> None:
    user_data = await get_user_by_tg_id(callback.from_user.id)
    if user_data.role == UserRole.ADMIN or user_data.role == UserRole.WORKER:
        if server_provider == ServerProvider.VULTR:
            wait_msg = await callback.message.answer("🤖💬Пожалуйста, подождите, идет загрузка...")
            server_data = await choose_server_before_buying(server_provider)
            provider = "Vultr"
            plan = server_data.plan_id
            cpu_vendor = server_data.cpu_vendor
            vcpu_count = server_data.vcpu_count
            ram = server_data.ram
            disk = server_data.disk
            disk_type = server_data.disk_type
            disk_count = server_data.disk_count
            bandwidth = server_data.bandwidth
            monthly_cost = server_data.monthly_cost
            hourly_cost = server_data.hourly_cost
            server_type = server_data.type
            location_id = server_data.location_id
            os_id = "Ubuntu 22.04 x64" if server_data.os_id == 1743 else str(server_data.os_id)
            region_name = server_data.region_name

            await state.update_data(
                provider=ServerProvider.VULTR,
                plan=plan,
                cpu_vendor=cpu_vendor,
                vcpu_count=vcpu_count,
                ram=ram,
                disk=disk,
                disk_type=disk_type,
                disk_count=disk_count,
                bandwidth=bandwidth,
                monthly_cost=monthly_cost,
                hourly_cost=hourly_cost,
                type=server_type,
                location_id=location_id,
                os_id=os_id,
                region_name=region_name
            )

            info_msg = f"""
==============================
🌐 <b>Вы покупаете сервер</b> 🌐
==============================
🛜 <b>Провайдер: <code>{provider}</code></b>
📦 <b>План: <code>{plan}</code></b>
🖥️ <b>CPU: <code>{cpu_vendor} {vcpu_count} vCPU</code></b>
💾 <b>RAM: <code>{ram} GB</code></b>
💽 <b>Диск: <code>{disk} GB {disk_type}</code></b>
🔢 <b>Количество дисков: <code>{disk_count}</code></b>
🚀 <b>Пропускная способность: <code>{bandwidth} Mbps</code></b>
💸 <b>Ежемесячная стоимость: <code>${monthly_cost}</code></b>
⏱️ <b>Почасовая стоимость: <code>${hourly_cost}</code></b>
🔖 <b>Тип: <code>{type}</code></b>
🖥️ <b>ОС: <code>{os_id}</code></b>
📍 <b>Регион: <code>{region_name}</code></b>
==============================
"""
            await wait_msg.delete()
            await callback.message.answer(
                text=info_msg,
                reply_markup=await select_buy_server_kb()
            )


async def success_buy_server(callback: CallbackQuery, server_id: str) -> None:
    # await callback.message.delete()
    server_data = await get_server_by_id(server_id)
    if not server_data:
        await callback.message.answer("Ошибка при получении данных сервера.")
        return
    server_info = await get_hosting(server_id)
    user_data = await get_user_by_tg_id(callback.from_user.id)
    info_msg = f"""
==============================
🌐 <b>{server_data.server_name}</b> 🌐
==============================
🆔 <b>ID: <code>{server_data.server_id}</code></b>
🛜 <b>Провайдер: <code>{server_data.server_provider}</code></b>
📦 <b>План: <code>{server_info.plan_id}</code></b>
🖥️ <b>ОС: <code>{server_info.os}</code></b>
📍 <b>Регион: <code>{server_data.server_region}</code></b>
==============================
🖥️ <b>IP сервера: <code>{server_data.server_ip}</code></b>
🔑 <b>Пароль: <code>{server_data.server_password}</code></b>
🌐 <b>SFTP/HestiaCP: <a href="{server_data.hestia_url}">{server_data.hestia_url}</a></b>
┣ <b>Логин: <code>{user_data.hestia_username}</code></b>
┗ <b>Пароль: <code>{user_data.hestia_password}</code></b>
"""

    await callback.message.answer(text=info_msg)


async def buy_server_and_create(callback: CallbackQuery, provider: ServerProvider) -> None:
    server_data = await choose_server_before_buying(provider)

    if provider == ServerProvider.VULTR:
        worker_data = await get_user_by_tg_id(callback.from_user.id)

        plan = server_data.plan_id
        region = server_data.location_id
        os_id = server_data.os_id
        tags = f'@{worker_data.username}'

        region_name = server_data.region_name
        servers = await get_all_servers()
        number_new_server = len(servers) + 1
        today_str = datetime.now().strftime("%d-%m-%Y")
        label = f'Serv-{number_new_server} ({region_name}) ({today_str})'

        email = EMAIL
        hestia_username = worker_data.hestia_username
        hestia_password = worker_data.hestia_password
        # FTP_username = worker_data.FTP_username
        # FTP_password = worker_data.FTP_password
        # username: str, password: str, email: str, user_tg_id: int, bot_token: str, label: str
        user_data = encode_hestia_script(
            username=hestia_username,
            password=hestia_password,
            email=email,
            user_tg_id=worker_data.tg_id,
            bot_token=BOT_TOKEN,
            label=label
        )

        new_server = await create_hosting(
            region=region,
            plan=plan,
            os_id=os_id,
            user_data=user_data,
            label=label,
            tags=[tags]
        )
        print(new_server)
        await asyncio.sleep(10)  # Ждем 10 секунд чтобы сервер успел создаться
        server_password = new_server.server_password

        new_server = await get_hosting(new_server.server_id)
        attempts = 0
        max_attempts = 12  # например, максимум 2 минуты ожидания

        while new_server.main_ip == "0.0.0.0" and attempts < max_attempts:
            await asyncio.sleep(10)
            new_server = await get_hosting(new_server.server_id)
            attempts += 1

        if new_server.main_ip != "0.0.0.0":
            print(f"Сервер создан с IP: {new_server.main_ip}")
            print(new_server)
            await create_server(server_data=ServerCreateSchema(
                user_id=worker_data.tg_id,
                server_id=new_server.server_id,
                server_ip=new_server.main_ip,
                server_region=region_name,
                server_name=label,
                server_tag=tags,
                server_password=server_password,
                hestia_url=f'https://{new_server.main_ip}:8083/'
            ))


async def get_info_server_menu(callback: CallbackQuery, server_id: str) -> None:
    await callback.answer()
    print(f"Получение информации по серверу {server_id}")
    server_data = await get_server_by_id(server_id)
    print(server_data)
    if not server_data:
        await callback.message.answer("Ошибка при получении данных сервера.")
        return
    user_data = await get_user_by_tg_id(server_data.user_id)
    active_domains = await get_active_domains_by_server_id(server_id)
    count_active_domains = len(active_domains)
    # Формируем список доменов с SSL-статусом
    if active_domains:
        domain_list = "\n".join(
            f"┗ {domain.domain_name} | SSL {'🟢' if domain.ssl_activated else '🔴'}"
            for domain in active_domains
        )
    else:
        domain_list = "Нет активных доменов."
    # 🚀<b>Status: <code>{server_info.status}/{server_info.power_status}/{server_info.server_status}</code></b>
    # 🆔 <b>ID: <code>{server_data.server_id}</code></b>
    # 🛜 <b>Провайдер: <code>{server_data.server_provider}</code></b>
    # 🖥️ <b>ОС: <code>{server_info.os}</code></b>
    # ==============================
    # 🖥️ <b>IP сервера: <code>{server_data.server_ip}</code></b>
    # 🔑 <b>Пароль: <code>{server_data.server_password}</code></b>
    if user_data.tg_id != callback.from_user.id:
        header = f"Сервер принадлежит @{user_data.username} (ID: {user_data.tg_id})"
    else:
        header = "Ваш сервер"

    msg = f"""
{header}
==============================
🌐 <b>{server_data.server_name}</b> 
==============================
🖥️ <b>IP сервера: <code>{server_data.server_ip}</code></b>
==============================
🌐 <b>SFTP/HestiaCP: <a href="{server_data.hestia_url}">{server_data.hestia_url}</a></b>
┣ <b>Логин: <code>{user_data.hestia_username}</code></b>
┗ <b>Пароль: <code>{user_data.hestia_password}</code></b>
==============================
🏧<b>Домены: {count_active_domains}/{server_data.max_domains}</b>
{domain_list}
==============================
"""

    await callback.message.answer(text=msg,
                                  reply_markup=await get_server_menu_kb(server_id, callback.from_user.id)
                                  )


async def delete_server_func(callback: CallbackQuery, server_id: str):
    server_data = await get_server_by_id(server_id)
    if not server_data:
        await callback.answer("Сервер не найден!", show_alert=True)
        return
    active_domains = await get_active_domains_by_server_id(server_id)
    if active_domains:
        domain_lines = [
            f"┗ {domain.domain_name} | SSL {'🟢' if domain.ssl_activated else '🔴'}"
            for domain in active_domains
        ]
        domain_list = (
                "<b>На сервере есть активные домены:</b>\n"
                "(Данные домены будут переведены в статус «неактивен» при удалении сервера)\n\n"
                + "\n".join(domain_lines)
        )
    else:
        domain_list = "<b>На сервере нет активных доменов.</b>"
    msg = f"""
==============================
Подтвердите удаление сервера:
<b>*{server_data.server_name}*</b>.

{domain_list}
==============================
"""
    await callback.message.answer(
        text=msg,
        reply_markup=await get_confirm_delete_server_kb(server_id)
    )


async def confirm_delete_server_func(callback: CallbackQuery, server_id: str):
    server_data = await get_server_by_id(server_id)
    if not server_data:
        await callback.answer("Сервер не найден!", show_alert=True)
        return

    await delete_hosting(server_data.server_id)
    max_attempts = 60
    attempts = 0
    while True:
        result = await get_hosting(server_data.server_id)
        if result is None:
            break
        await asyncio.sleep(1)
        attempts += 1
        if attempts >= max_attempts:
            await callback.message.answer("❗️Сервер не был удалён за отведённое время. Попробуйте позже.")
            return

    await update_server_status(server_id, ServerStatus.DELETED)
    active_domains = await get_active_domains_by_server_id(server_id)
    for domain in active_domains:
        await update_domain_status(domain.id, DomainStatus.DELETED)
    await send_servers_menu(callback)


async def get_active_users_for_reassign_server(callback: CallbackQuery, server_id: str):
    server = await get_server_by_id(server_id)
    if not server:
        await callback.message.answer("Сервер не найден.")
        return
    await callback.message.answer(
        text=f"🌐 <b>Выберите пользователя для передачи сервера {server.server_name}:</b>",
        reply_markup=await get_users_list_for_reassign_kb(server.user_id, server_id)
    )


async def reassign_server_owner_func(callback: CallbackQuery, server_id: str, new_owner_id: int):
    server = await get_server_by_id(server_id)
    if not server:
        await callback.message.answer("Сервер не найден.")
        return
    old_owner_id = server.user_id
    if old_owner_id == new_owner_id:
        await callback.answer("Нельзя переназначить сервер тому же владельцу!", show_alert=True)
        return
    old_user_data = await get_user_by_tg_id(old_owner_id)
    new_user_data = await get_user_by_tg_id(new_owner_id)
    if not old_user_data or not new_user_data:
        await callback.message.answer("Пользователь не найден.")
        return
    changed = await change_user_password(server.server_ip, server.server_password, old_user_data.hestia_username,
                                         new_user_data.hestia_password)
    print(changed)

    update_server_in_db = await reassign_server_owner(server_id, new_owner_id)
    print("Обновление статуса сервера в БД:", update_server_in_db)
    if not update_server_in_db:
        await callback.message.answer("Ошибка при обновлении владельца сервера в базе данных.")
        return

    active_domains_in_server = await get_active_domains_by_server_id(server_id)
    print("Активные домены на сервере:", active_domains_in_server)
    update_domains_in_db = True  # по умолчанию считаем, что всё ок, если доменов нет

    if active_domains_in_server:
        update_domains_in_db = await update_domains_user_ids_for_server(server_id, new_owner_id)
        print("Обновление user_id доменов в БД:", update_domains_in_db)
        if not update_domains_in_db:
            await callback.message.answer("Ошибка при обновлении владельца доменов в базе данных.")
            return

    msg_info = f"""
==============================
🌐 <b>Сервер переназначен</b> 🌐
"""
    await callback.message.answer(text=msg_info)
    await get_info_server_menu(callback, server_id)
