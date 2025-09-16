from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import (
    ADMIN_TG_ID, 
    FTP_USERNAME, 
    HESTIA_USERNAME
)
from outboxes.start import (
    send_need_username,
    send_admin_registered,
    send_request_to_admin,
    send_welcome
)
from utils.database.services.user import (
    create_user,
    get_user_by_tg_id
)
from utils.password_generator import generate_password
from utils.schemas.user_db import (
    UserCreateSchema,
    UserRole
)

router = Router()

@router.message(F.text == "⬅️Назад")
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username

    if not username:
        await send_need_username(message)
        return

    user = await get_user_by_tg_id(user_id)

    if user is None:
        password = generate_password()
        if user_id == ADMIN_TG_ID:
            await create_user(UserCreateSchema(
                tg_id=user_id,
                username=username,
                role=UserRole.ADMIN,
                hestia_password=password,
                hestia_username=HESTIA_USERNAME, 
                FTP_username=FTP_USERNAME,
                FTP_password=password
            ))
            await send_admin_registered(message)
        else:
            await create_user(UserCreateSchema(
                tg_id=user_id,
                username=username,
                role=UserRole.USER,
                hestia_password=password,
                hestia_username=HESTIA_USERNAME, 
                FTP_username=FTP_USERNAME,
                FTP_password=password
            ))
            await send_request_to_admin(
                message.bot,
                ADMIN_TG_ID,
                username,
                user_id
            )
            await message.answer("Заявка отправлена администратору. Ожидайте подтверждения, или свяжитесь с администратором напрямую: @Jumper01.")
        return

    if user.role == UserRole.USER:
        await message.answer("Ваша заявка всё ещё на рассмотрении. Ожидайте или свяжитесь с администратором напрямую: @Jumper01.")
        return

    if user.role in (UserRole.WORKER, UserRole.ADMIN):
        await send_welcome(message)