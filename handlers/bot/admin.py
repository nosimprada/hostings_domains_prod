from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.admin_kb import build_users_keyboard
from keyboards.start_kb import get_start_keyboard
from middlewares.admin_check import AdminCheckMiddleware
from outboxes.admin import get_active_domains_by_user_id_for_admin, get_active_servers_by_user_id_for_admin, \
    send_active_users_menu, send_info_about_users
from outboxes.start import get_main_msg
from utils.database.services.user import (
    block_user, get_all_active_users, get_user_by_tg_id, update_user_role_worker
)


class BlockUserState(StatesGroup):
    confirm_block = State()


router = Router()
router.message.middleware(AdminCheckMiddleware())
router.callback_query.middleware(AdminCheckMiddleware())


@router.callback_query(F.data.startswith("approve_request_"))
async def approve_request_handler(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await update_user_role_worker(user_id)
    old_text = callback.message.text or ""
    new_text = f"{old_text}\n\n✅ Одобрено"
    await callback.message.edit_text(new_text)
    await callback.answer("")
    await callback.bot.send_message(chat_id=user_id, text=await get_main_msg(user_id),
                                    reply_markup=await get_start_keyboard(user_id)
                                    )
    await callback.bot.send_message(chat_id=callback.from_user.id, text=await get_main_msg(callback.from_user.id),
                                    reply_markup=await get_start_keyboard(callback.from_user.id)
                                    )


@router.callback_query(F.data.startswith("block_request_"))
async def block_request_handler(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await block_user(user_id)
    old_text = callback.message.text or ""
    new_text = f"{old_text}\n\n❌ Отклонено"
    await callback.message.edit_text(new_text)
    await callback.answer("")
    await callback.bot.send_message(
        user_id,
        "Ваша заявка отклонена или вы заблокированы администратором."
    )


@router.callback_query(F.data == "workers")
async def workers_handler(callback: CallbackQuery):
    await send_active_users_menu(callback)


@router.callback_query(F.data.startswith("user_"))
async def user_info_handler(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await send_info_about_users(callback, user_id)


@router.callback_query(F.data.startswith("users_page_"))
async def users_pagination_handler(callback: CallbackQuery):
    page = int(callback.data.split("_")[-1])
    users = await get_all_active_users()
    markup = await build_users_keyboard(callback, users, page=page)
    await callback.message.edit_reply_markup(reply_markup=markup)
    await callback.answer()


@router.callback_query(F.data.startswith("servers_user_"))
async def servers_info_handler(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await get_active_servers_by_user_id_for_admin(callback, user_id)


@router.callback_query(F.data.startswith("domains_user_"))
async def domains_info_handler(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await get_active_domains_by_user_id_for_admin(callback, user_id)


@router.callback_query(F.data.startswith("blocked_user_"))
async def blocked_user_info_handler(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    user_data = await get_user_by_tg_id(user_id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Подтвердить",
        callback_data=f"confirm_block_{user_id}"
    )
    builder.button(
        text="❌ Отменить",
        callback_data=f"user_{user_id}"
    )
    builder.adjust(2)
    await callback.message.answer(
        f"Вы уверены, что хотите заблокировать @{user_data.username}?",
        reply_markup=builder.as_markup()  # <-- исправление здесь
    )


@router.callback_query(F.data.startswith("confirm_block_"))
async def confirm_block_user_info_handler(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])
    await block_user(user_id)
    await callback.answer()
    await callback.bot.send_message(
        user_id,
        "Вы были заблокированы администратором."
    )
    old_text = callback.message.text or ""
    new_text = f"{old_text}\n\n✅ Заблокирован"
    await callback.message.edit_text(new_text)
    await send_active_users_menu(callback)
