from aiogram.types import InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from api.vultr import get_hosting
from utils.database.services.domain import get_active_domains_by_server_id
from utils.database.services.server import get_server_by_id, \
    get_active_servers_without_created_at_by_user_id
from utils.database.services.user import get_user_by_tg_id
from utils.schemas.server_db import ServerProvider
from utils.schemas.user_db import UserRole


async def get_reply_server_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="➕Купить сервер")
    builder.button(text="⬅️Назад")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def get_info_servers_menu_kb(user_id: int, page: int = 0, per_page: int = 10,
                                   admin: bool = False) -> InlineKeyboardMarkup:
    providers_list = ServerProvider
    builder = InlineKeyboardBuilder()
    servers = await get_active_servers_without_created_at_by_user_id(user_id)
    if not admin:
        for provider in providers_list:
            builder.button(
                text=f"🚀Купить сервер {provider.value} + HestiaCP",
                callback_data=f"buy_server_provider_{provider.name}"
            )

    if servers:
        start = page * per_page
        end = start + per_page
        page_servers = servers[start:end]
        for server in page_servers:
            host_data = await get_hosting(server.server_id)
            active_domains = await get_active_domains_by_server_id(server.server_id)
            count_active_domains = len(active_domains)
            print(host_data)
            server_status = "🟢" if host_data and host_data.status == "active" else "⚠️"
            builder.button(
                text=f"{server.server_name} ({count_active_domains}/{server.max_domains}) {server_status}",
                callback_data=f"server_{server.server_id}"
            )

        # Кнопки пагинации
        total_pages = (len(servers) - 1) // per_page + 1
        pagination_buttons = []
        if page > 0:
            pagination_buttons.append(
                {"text": "⬅️", "callback_data": f"servers_page_{page - 1}"}
            )
        if page < total_pages - 1:
            pagination_buttons.append(
                {"text": "➡️", "callback_data": f"servers_page_{page + 1}"}
            )
        if pagination_buttons:
            from aiogram.types import InlineKeyboardButton
            builder.row(*[InlineKeyboardButton(**btn) for btn in pagination_buttons])
    if admin:
        builder.button(text="🔙 Назад", callback_data=f"user_{user_id}")

    builder.button(text="🏡 На главную", callback_data="back_to_start")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def get_menu_last_buy_server_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="К списку серверов", callback_data="servers")
    builder.button(text="На главную🏡", callback_data="back_to_start")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def get_list_providers_kb() -> InlineKeyboardMarkup:
    providers_list = ServerProvider
    builder = InlineKeyboardBuilder()
    for provider in providers_list:
        builder.button(text=provider.value, callback_data=f"provider_{provider.name}")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def select_buy_server_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Купить📥", callback_data=f"buy_server")
    builder.button(text="Обновить регион🌍", callback_data=f"refresh_server")
    builder.button(text="Отмена🚫", callback_data="cancel_buy_server")
    builder.adjust(1)
    return builder.as_markup()


async def get_server_menu_kb(server_id: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    server_data = await get_server_by_id(server_id)
    count_active_domains = len(await get_active_domains_by_server_id(server_id))
    max_domains = server_data.max_domains if server_data else 0
    owner_id = server_data.user_id
    user_data = await get_user_by_tg_id(user_id)

    # Кнопки изменения max_domains
    # -5
    if max_domains - 5 >= count_active_domains:
        builder.button(text="-5", callback_data=f"change_max_domains_{server_id}_-5")
    else:
        builder.button(text="-5🚫", callback_data="noop")
    # -1
    if max_domains - 1 >= count_active_domains:
        builder.button(text="-1", callback_data=f"change_max_domains_{server_id}_-1")
    else:
        builder.button(text="-1🚫", callback_data="noop")
    # +1
    builder.button(text="+1", callback_data=f"change_max_domains_{server_id}_+1")
    # +5
    builder.button(text="+5", callback_data=f"change_max_domains_{server_id}_+5")

    builder.button(text="Удалить сервер❌", callback_data=f"delete_server_{server_id}")
    if user_data.role == UserRole.ADMIN:
        builder.button(text="Переназначить владельца👤", callback_data=f"reassign_server_{server_id}")
    if owner_id == user_id:
        builder.button(text="🔙 Назад", callback_data="servers")
    else:

        builder.button(text="🔙 Назад", callback_data=f"servers_user_{owner_id}")
    builder.button(text="🏡 На главную", callback_data="back_to_start")
    builder.adjust(4, 1, 1, 1)  # 4 кнопки в первой строке, остальные по одной
    return builder.as_markup()


async def get_confirm_delete_server_kb(server_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Да, удалить❌", callback_data=f"confirm_delete_server_{server_id}")
    builder.button(text="Отмена🚫", callback_data=f"server_{server_id}")
    builder.adjust(1)
    return builder.as_markup()


async def get_users_list_for_reassign_kb(current_owner_id: int, server_id: str) -> InlineKeyboardMarkup:
    from utils.database.services.user import get_all_active_users
    users = await get_all_active_users()
    builder = InlineKeyboardBuilder()
    for user in users:
        if user.tg_id != current_owner_id:
            username = user.username or "Без username"
            tg_id = user.tg_id
            btn_text = f"@{username} | {tg_id}"
            builder.button(
                text=btn_text,
                callback_data=f"reassignser_{server_id}_to_{tg_id}"
            )

    builder.button(text="🔙 Назад", callback_data=f"server_{server_id}")
    builder.adjust(1)
    return builder.as_markup()
