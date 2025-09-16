from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Awaitable, Dict, Any

from utils.database.services.user import get_user_by_tg_id  
from utils.schemas.user_db import UserRole  

class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        user = await get_user_by_tg_id(user_id)
        if not user or user.role != UserRole.ADMIN:
            if isinstance(event, Message):
                await event.answer("⛔️ У вас нет доступа к этой функции.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⛔️ У вас нет доступа.", show_alert=True)
            return
        return await handler(event, data)