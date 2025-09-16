from aiogram.types import InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.database.services.domain import get_active_domains_by_user_id
from utils.database.services.server import get_active_servers_by_user_id


async def build_users_keyboard(callback: CallbackQuery, users, page: int = 0,
                               per_page: int = 8) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start = page * per_page
    end = start + per_page
    page_users = users[start:end]

    for user in page_users:
        if callback.from_user.id == user.tg_id:
            continue

        username = user.username or "Без username"
        tg_id = user.tg_id
        btn_text = f"@{username} | {tg_id}"
        builder.button(
            text=btn_text,
            callback_data=f"user_{tg_id}"
        )

    # Пагинация
    pagination = []
    total_pages = (len(users) - 1) // per_page + 1
    if page > 0:
        pagination.append({"text": "⬅️", "callback_data": f"users_page_{page - 1}"})
    if page < total_pages - 1:
        pagination.append({"text": "➡️", "callback_data": f"users_page_{page + 1}"})

    if pagination:
        from aiogram.types import InlineKeyboardButton
        buttons = [InlineKeyboardButton(**btn) for btn in pagination]
        builder.row(*buttons)

    builder.button(text="🏡 На главную", callback_data="back_to_start")
    builder.adjust(1)
    return builder.as_markup()


async def set_user_kb(user_id) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    count_active_servers = len(await get_active_servers_by_user_id(user_id))
    count_active_domains = len(await get_active_domains_by_user_id(user_id))
    if count_active_servers > 0:
        builder.button(text=f"🌐Сервера ({count_active_servers})", callback_data=f"servers_user_{user_id}")
    if count_active_domains > 0:
        builder.button(text=f"🏧Домены ({count_active_domains})", callback_data=f"domains_user_{user_id}")
    builder.button(text="❌ Заблокировать", callback_data=f"blocked_user_{user_id}")
    builder.button(text="🔙 Назад", callback_data="workers")
    builder.button(text="🏡 На главную", callback_data="back_to_start")
    builder.adjust(1)
    return builder.as_markup()
