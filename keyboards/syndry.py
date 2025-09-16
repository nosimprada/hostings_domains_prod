from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

async def get_menu_back_to_domains_and_home() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="servers")
    builder.button(text="🏡 На главную", callback_data="back_to_start")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)