from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from utils.database.services.user import get_user_by_tg_id
from utils.schemas.user_db import UserRole

async def get_start_keyboard(user_id: int) -> InlineKeyboardMarkup:
    user = await get_user_by_tg_id(user_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="🗄Домены🏧", callback_data="domains")
    builder.button(text="🗄Сервера🌐", callback_data="servers")
    if user.role == UserRole.ADMIN:
        builder.button(text="🧑‍💻Работники⚙️", callback_data="workers")
    builder.button(text="🛠Настройки⚙️", callback_data="settings")

    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

async def get_send_request_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Одобрить✅", callback_data=f"approve_request_{user_id}")
    builder.button(text="В блок❌", callback_data=f"block_request_{user_id}")
    builder.adjust(1)
    return builder.as_markup()


