from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


async def get_settings_namecheap_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤API_KEY⚙️", callback_data="set_namecheap_api_key")
    builder.button(text="🔑API_USER⚙️", callback_data="set_namecheap_api_user")
    builder.button(text="На главную🏡", callback_data="back_to_start")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

async def get_back_to_settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="settings")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)