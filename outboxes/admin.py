from aiogram.types import CallbackQuery

from keyboards.admin_kb import (
    build_users_keyboard,
    set_user_kb
)
from keyboards.domains_kb import get_domains_menu_kb
from keyboards.servers_kb import get_info_servers_menu_kb
from utils.database.services.domain import get_active_domains_by_user_id
from utils.database.services.server import (
    get_active_servers_by_user_id
)
from utils.database.services.user import (
    get_all_active_users,
    get_user_by_tg_id,
)


async def send_active_users_menu(callback: CallbackQuery):
    users = await get_all_active_users()
    if not users:
        await callback.answer("Нет активных пользователей.")
        return
    count_active_users = len(users)
    msg = f"""
==============================
🧑‍💻<b>Активные пользователи: <code>{count_active_users}</code>🙋‍♂️</b>
==============================
"""
    await callback.message.answer(text=msg, reply_markup=await build_users_keyboard(callback, users))


async def send_info_about_users(callback: CallbackQuery, user_id: int):
    user = await get_user_by_tg_id(user_id)
    if not user:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return
    count_active_servers = len(await get_active_servers_by_user_id(user.tg_id))
    count_active_domains = len(await get_active_domains_by_user_id(user.tg_id))
    msg = f"""
==============================
🧑‍💻 <b>Информация о пользователе:</b>
==============================
🆔 <b>ID: <code>{user.tg_id}</code></b>
🏷️ <b>Тэг: @{user.username}</b>
👤 <b>Роль: <code>{user.role}</code></b>
🖥️ <b>Серверов (Активных): <code>{count_active_servers}</code></b>
🌐 <b>Доменов (Активных): <code>{count_active_domains}</code></b>
==============================
"""
    await callback.message.answer(text=msg, reply_markup=await set_user_kb(user.tg_id))


async def get_active_servers_by_user_id_for_admin(callback: CallbackQuery, user_id: int):
    user_data = await get_user_by_tg_id(user_id)
    count_active_servers = len(await get_active_servers_by_user_id(user_id))
    msg_info = f"""
==============================
<b>Серверы пользователя:</b>
<b>@{user_data.username} | <code>{user_data.tg_id}</code></b>
==============================
Активных серверов: {count_active_servers}
==============================
"""
    await callback.message.answer(msg_info, reply_markup=await get_info_servers_menu_kb(user_id, admin=True))


async def get_active_domains_by_user_id_for_admin(callback: CallbackQuery, user_id: int):
    user_data = await get_user_by_tg_id(user_id)
    count_active_domains = len(await get_active_domains_by_user_id(user_id))
    msg_info = f"""
==============================
<b>Домены пользователя:</b>
<b>@{user_data.username} | <code>{user_data.tg_id}</code></b>
==============================
Активных доменов: {count_active_domains}
==============================
"""
    await callback.message.answer(msg_info, reply_markup=await get_domains_menu_kb(user_id, admin=True))
