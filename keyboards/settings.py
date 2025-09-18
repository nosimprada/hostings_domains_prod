from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from api import dynadot, namecheap
from config import CLIENT_IP
from utils.database.services.user import get_user_by_tg_id

async def get_settings_main_kb(user_id) -> InlineKeyboardMarkup:

    user_data = await get_user_by_tg_id(user_id)
    namecheap_api_balance = await namecheap.get_user_balance(
        api_user=user_data.namecheap_api_user,
        api_key=user_data.namecheap_api_key,
        api_username=user_data.namecheap_api_user,
        api_client_ip=CLIENT_IP
    )
    dynadot_api_balance = await dynadot.get_user_balance(api_key=user_data.dynadot_api_key)
    namecheap_status = "🟢" if namecheap_api_balance is not None else "⚠️"
    dynadot_status = "🟢" if dynadot_api_balance is not None else "⚠️"

    builder = InlineKeyboardBuilder()
    builder.button(text=f"⚙️Namecheap {namecheap_status}", callback_data="settings_namecheap")
    builder.button(text=f"⚙️Dynadot {dynadot_status}", callback_data="settings_dynadot")
    builder.button(text="На главную🏡", callback_data="back_to_start")
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)

async def get_settings_namecheap_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤API_KEY⚙️", callback_data="set_namecheap_api_key")
    builder.button(text="🔑API_USER⚙️", callback_data="set_namecheap_api_user")
    builder.button(text="🔙 Назад", callback_data="settings")
    builder.button(text="На главную🏡", callback_data="back_to_start")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

async def get_back_to_namecheap_settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="settings_namecheap")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

async def get_back_to_dynadot_settings_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Назад", callback_data="settings_dynadot")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

async def get_settings_dynadot_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤API_KEY⚙️", callback_data="set_dynadot_api_key")
    builder.button(text="🔙 Назад", callback_data="settings")
    builder.button(text="На главную🏡", callback_data="back_to_start")
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)