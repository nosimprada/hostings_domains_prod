from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from typing import Callable, Awaitable, Any
from utils.database.services.user import get_user_by_tg_id

class BlockCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, dict], Awaitable[Any]],
        event: Message,
        data: dict
    ) -> Any:
        user_id = event.from_user.id
        user = await get_user_by_tg_id(user_id)
        if user and getattr(user, "is_blocked", False):
            await event.answer("Ваш аккаунт заблокирован.")
            return  
        return await handler(event, data)