from aiogram import Bot
from aiogram.types import Message

from api.namecheap import get_user_balance
from config import CLIENT_IP
from keyboards.start_kb import (
    get_send_request_keyboard,
    get_start_keyboard,
)
from utils.database.services.domain import get_active_domains_by_user_id, get_all_active_domains
from utils.database.services.server import (
    get_active_servers_by_user_id,
    get_all_active_servers
)
from utils.database.services.user import get_user_by_tg_id, get_all_active_users
from utils.schemas.user_db import UserRole


async def get_main_msg(user_id: int):
    user_data = await get_user_by_tg_id(user_id)
    namecheap_balance = "Нет подключения ⚠️"

    msg: str = ""

    if user_data.role == UserRole.ADMIN:
        servers = await get_active_servers_by_user_id(user_id)
        count_active_servers = len(servers)

        all_domains = await get_all_active_domains()
        count_all_active_domains = len(all_domains)

        all_servers = await get_all_active_servers()
        count_all_active_servers = len(all_servers)

        domains = await get_active_domains_by_user_id(user_id)
        count_active_domains = len(domains)

        workers = await get_all_active_users()
        count_active_workers = len(workers)

        balance = await get_user_balance(
            api_user=user_data.namecheap_api_user,
            api_key=user_data.namecheap_api_key,
            api_username=user_data.namecheap_api_user,
            api_client_ip=CLIENT_IP
        )

        if balance is not None:
            namecheap_balance = f"{balance}$ 🟢"
        msg = f"""
==============================
🧑‍💻<b>Tag: <code>@{user_data.username}</code></b>
🆔<b>TG_ID: <code>{user_data.tg_id}</code></b>
🏧<b>Домены: {count_active_domains} / Всего: {count_all_active_domains}</b>
🌐<b>Сервера: {count_active_servers} / Всего: {count_all_active_servers}</b>
➡️<b>Namecheap (Личный): {namecheap_balance}</b>
==============================
<b>📁HestiaCP/SFTP:</b>
<b>┣ <code>{user_data.hestia_username}</code></b>
<b>┗ <code>{user_data.hestia_password}</code></b>
==============================
🙋‍♂️<b>Работники: {count_active_workers}</b>
==============================
"""
    elif user_data.role == UserRole.WORKER:
        servers = await get_active_servers_by_user_id(user_id)
        count_active_servers = len(servers)

        domains = await get_active_domains_by_user_id(user_id)
        count_active_domains = len(domains)

        # Для WORKER тоже пробуем получить баланс
        balance = await get_user_balance(
            api_user=user_data.namecheap_api_user,
            api_key=user_data.namecheap_api_key,
            api_username=user_data.namecheap_api_user,
            api_client_ip=CLIENT_IP
        )

        if balance is not None:
            namecheap_balance = f"{balance}$ 🟢"
        msg = f"""
==============================
🧑‍💻<b>Tag: <code>@{user_data.username}</code></b>
🆔<b>TG_ID: <code>{user_data.tg_id}</code></b>
🏧<b>Домены: {count_active_domains}</b>
🌐<b>Сервера: {count_active_servers}</b>
➡️<b>Namecheap: {namecheap_balance}</b>
==============================
<b>📁HestiaCP/SFTP:</b>
<b>┣ <code>{user_data.hestia_username}</code></b>
<b>┗ <code>{user_data.hestia_password}</code></b>
==============================
"""
    return msg


async def send_need_username(message: Message):
    await message.answer("Для использования бота необходимо установить username в настройках Telegram.")


async def send_admin_registered(message: Message):
    await message.answer(
        text=await get_main_msg(message.from_user.id),
        reply_markup=await get_start_keyboard(message.from_user.id)
    )


async def send_request_to_admin(bot: Bot, admin_id: int, username: str, user_id: int):
    await bot.send_message(
        admin_id,
        f"Новая заявка на регистрацию:\n@{username} (id: {user_id})",
        reply_markup=await get_send_request_keyboard(user_id)
    )


async def send_welcome(message: Message):
    await message.answer(
        text=await get_main_msg(message.from_user.id),
        reply_markup=await get_start_keyboard(message.from_user.id)
    )
