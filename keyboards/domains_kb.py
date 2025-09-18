from typing import List

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from api import dynadot, namecheap
from config import CLIENT_IP
from outboxes.sundry import get_servers_with_free_slots
from utils.database.services.domain import get_active_domains_by_server_id, get_active_domains_by_user_id, \
    get_domain_by_id
from utils.database.services.user import get_user_by_tg_id
from utils.schemas.user_db import UserRole


async def back_domains_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="domains")
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)


async def get_menu_back_to_domains_and_home() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="servers")
    builder.button(text="🏡 На главную", callback_data="back_to_start")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def get_domains_menu_kb(user_id: int, page: int = 1, per_page: int = 8,
                              admin: bool = False) -> InlineKeyboardMarkup:
    print("Запрошена страница", page)

    domains = await get_active_domains_by_user_id(user_id)
    domains_sorted = sorted(domains, key=lambda d: (d.server_id is not None, d.domain_name))
    user_data = await get_user_by_tg_id(user_id)
    balance_dynadot = await dynadot.get_user_balance(api_key=user_data.dynadot_api_key)
    balance_namecheap = await namecheap.get_user_balance(
        api_user=user_data.namecheap_api_user,
        api_key=user_data.namecheap_api_key,
        api_username=user_data.namecheap_api_user,
        api_client_ip=CLIENT_IP
    )

    total = len(domains_sorted)

    start = (page - 1) * per_page
    end = start + per_page

    page_domains = domains_sorted[start:end]

    builder = InlineKeyboardBuilder()

    if not admin:
        if balance_dynadot is not None:
            builder.button(text="🚀 Купить домен Dynadot", callback_data="create_domain_dynadot")
        if balance_namecheap is not None:
            builder.button(text="🚀 Купить домен Namecheap", callback_data="create_domain_namecheap")

    for domain in page_domains:
        text = f"🏧 {domain.domain_name} (SSL:{'✅' if domain.ssl_activated else '❌'})"
        if not domain.server_id:
            text += " 🆕"
        builder.button(
            text=text,
            callback_data=f"domain_{domain.domain_id}"
        )

    # Пагинация
    nav_row: List = []

    if page > 1:
        if admin:
            nav_row.append({"text": "⬅️", "callback_data": f"admin_domains_page_{user_id}_{page - 1}"})
        else:
            nav_row.append({"text": "⬅️", "callback_data": f"domains_page_{page - 1}"})
    if end < total:
        if admin:
            nav_row.append({"text": "➡️", "callback_data": f"admin_domains_page_{user_id}_{page + 1}"})
        else:
            nav_row.append({"text": "➡️", "callback_data": f"domains_page_{page + 1}"})

    for nav in nav_row:
        builder.button(**nav)

    if admin:
        builder.button(text="🔙 Назад", callback_data=f"user_{user_id}")
    builder.button(text="🏡 На главную", callback_data="back_to_start")

    # Располагаем кнопки: домены по одной, навигация и действия отдельно
    adjust_args = [1]  # "Купить домен"
    adjust_args += [1] * len(page_domains)  # домены по 1 в ряд
    if nav_row:
        adjust_args.append(len(nav_row))  # пагинация, если есть
    adjust_args.append(1)  # "На главную"
    builder.adjust(*adjust_args)
    return builder.as_markup(resize_keyboard=True)


async def confirm_buy_domains_namecheap_kb(count_available: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if count_available > 0:
        builder.button(text="📥 Купить", callback_data="confirm_buy_domains_namecheap")
    builder.button(text="🔙 Назад", callback_data="domains")
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)

async def confirm_buy_domains_dynadot_kb(count_available: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if count_available > 0:
        builder.button(text="📥 Купить", callback_data="confirm_buy_domains_dynadot")
    builder.button(text="🔙 Назад", callback_data="domains")
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)


# Кнопка для выбора распределения доменов по слотам серверов автоматически или вручную
async def choose_domain_slot_distribution_kb(count_created: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if count_created >= 1:
        builder.button(text="🤖 Автоматически", callback_data="auto_distribute_domains")
    builder.button(text="🔙 Назад", callback_data="domains")
    builder.adjust(1, 1, 1)
    return builder.as_markup(resize_keyboard=True)


async def manage_domain_kb(domain_id: int, server_data: bool, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not server_data:
        user_data = await get_user_by_tg_id(user_id)
        builder.button(text="🔗 Привязать к серверу", callback_data=f"binding_{domain_id}")
        if user_data.role == UserRole.ADMIN:
            builder.button(text="👤 Переназначить владельца", callback_data=f"reassign_owner_{domain_id}")
    owner_data = await get_domain_by_id(domain_id)
    if user_id == owner_data.user_id:
        builder.button(text="🔙 Назад", callback_data=f"domains_user_{user_id}")
    else:
        builder.button(text="🔙 Назад", callback_data="domains")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def get_available_servers_for_domain_binding_kb(domain_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    owner_data = await get_domain_by_id(domain_id)
    available_servers = await get_servers_with_free_slots(owner_data.user_id)
    for server in available_servers:
        field_slot = await get_active_domains_by_server_id(server.server_id)
        builder.button(text=f"🖥️ {server.server_name} ({len(field_slot)}/{server.max_domains})🌐",
                       callback_data=f"bind_domain_{domain_id}_{server.server_id}")
    builder.button(text="🔙 Назад", callback_data="domains")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def get_users_list_for_reassign_kb(exclude_user_id: int, domain_id: int) -> InlineKeyboardMarkup:
    from utils.database.services.user import get_all_active_users
    users = await get_all_active_users()
    builder = InlineKeyboardBuilder()
    for user in users:
        if user.tg_id != exclude_user_id:
            username = user.username or "Без username"
            builder.button(text=f"@{username} | {user.tg_id}", callback_data=f"reassign_{domain_id}_to_{user.tg_id}")
    builder.button(text="🔙 Назад", callback_data=f"domain_{domain_id}")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
