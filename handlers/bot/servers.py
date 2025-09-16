from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.servers_kb import get_info_servers_menu_kb, get_menu_last_buy_server_kb
from keyboards.start_kb import get_start_keyboard
from outboxes.servers import (
    buy_server_and_create,
    confirm_delete_server_func,
    delete_server_func,
    get_active_users_for_reassign_server,
    get_choose_server_before_buying,
    get_info_server_menu,
    get_info_servers_menu,
    reassign_server_owner_func,
    send_servers_menu
)
from outboxes.start import get_main_msg
from utils.database.services.server import (
    get_server_by_id,
    get_server_by_ip,
    update_server_max_domains
)
from utils.schemas.server_db import ServerProvider

router = Router()


@router.callback_query(F.data == "servers")
async def cmd_servers(callback: CallbackQuery) -> None:
    await send_servers_menu(callback=callback)


@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery) -> None:
    await callback.message.answer(
        text=await get_main_msg(callback.from_user.id),
        reply_markup=await get_start_keyboard(callback.from_user.id)
    )


@router.callback_query(F.data.startswith("buy_server_provider_"))
async def buy_server_provider(callback: CallbackQuery) -> None:
    provider_name = callback.data.replace("buy_server_provider_", "")
    try:
        provider = ServerProvider[provider_name]
    except KeyError:
        await callback.answer("Неизвестный провайдер!", show_alert=True)
        return
    msg_answer = f"""
==============================
🚀Начинаю создание сервера на <b>{provider}</b> с панелью Hestia....

Пожалуйста подождите. Это может занять до 10 минут. 
После установки Вы получите уведомление. 
==============================
"""
    # await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text=msg_answer, reply_markup=await get_menu_last_buy_server_kb())
    await buy_server_and_create(callback, provider)


@router.callback_query(F.data.startswith("servers_page_"))
async def servers_pagination(callback: CallbackQuery) -> None:
    page_str = callback.data.replace("servers_page_", "")
    try:
        page = int(page_str)
    except ValueError:
        await callback.answer("Некорректный номер страницы!", show_alert=True)
        return
    await callback.message.edit_text(
        text=await get_info_servers_menu(callback.from_user.id),
        reply_markup=await get_info_servers_menu_kb(callback.from_user.id, page=page)
    )


@router.callback_query(F.data.startswith("server_ip_"))
async def server_ip_details(callback: CallbackQuery):
    server_ip = callback.data.replace("server_ip_", "")
    print(f"server_ip: {server_ip}")
    server_data = await get_server_by_ip(server_ip)
    if not server_data:
        await callback.answer("Сервер не найден!", show_alert=True)
        return
    await get_info_server_menu(callback, server_data.server_id)


@router.callback_query(F.data.startswith("server_"))
async def server_details(callback: CallbackQuery):
    server_id = callback.data.replace("server_", "")
    print(f"server_id: {server_id}")
    await get_info_server_menu(callback, server_id)


@router.callback_query(F.data.startswith("change_max_domains_"))
async def change_max_domains(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) < 5:
        await callback.answer("Некорректные данные!", show_alert=True)
        return
    server_id = parts[3]
    delta = parts[4]  # будет строка, например '-5', '+1', и т.д.

    server_data = await get_server_by_id(server_id)
    if not server_data:
        await callback.answer("Сервер не найден!", show_alert=True)
        return
    new_max_domains = server_data.max_domains + int(delta)
    if new_max_domains < 1:
        await callback.answer("Максимальное количество доменов не может быть меньше 1!", show_alert=True)
        return
    await update_server_max_domains(server_data.id, new_max_domains)
    await get_info_server_menu(callback, server_id)


@router.callback_query(F.data.startswith("delete_server_"))
async def delete_server(callback: CallbackQuery):
    server_id = callback.data.replace("delete_server_", "")
    await delete_server_func(callback, server_id)


@router.callback_query(F.data.startswith("confirm_delete_server_"))
async def confirm_delete_server(callback: CallbackQuery):
    server_id = callback.data.replace("confirm_delete_server_", "")
    await confirm_delete_server_func(callback, server_id)


# @router.message(F.text == "➕Купить сервер")
# async def cmd_buy_server(message: Message) -> None:
#     await get_providers_list(message)

# @router.callback_query(F.data.startswith("provider_"))
# async def provider_callback_handler(callback: CallbackQuery, state: FSMContext) -> None:
#     provider_name = callback.data.replace("provider_", "")
#     try:
#         provider = ServerProvider[provider_name]
#     except KeyError:
#         await callback.answer("Неизвестный провайдер!", show_alert=True)
#         return
#     await callback.message.edit_reply_markup(reply_markup=None)
#     await get_choose_server_before_buying(callback, provider, state)

@router.callback_query(F.data == "refresh_server")
async def refresh_server(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    provider = data.get('provider')
    await callback.message.delete()
    await state.clear()
    await get_choose_server_before_buying(callback, provider, state)


@router.callback_query(F.data == "cancel_buy_server")
async def cancel_buy_server(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.delete()
    await state.clear()
    await send_servers_menu(callback=callback)


@router.callback_query(F.data == "buy_server")
async def buy_server(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_reply_markup(reply_markup=None)
    await buy_server_and_create(callback, state)


@router.callback_query(F.data.startswith("reassign_server_"))
async def reassign_server(callback: CallbackQuery):
    server_id = callback.data.replace("reassign_server_", "")
    await get_active_users_for_reassign_server(callback, server_id)


@router.callback_query(F.data.startswith("reassignser_"))
async def reassign_server_handler(callback: CallbackQuery):
    server_id, new_owner_id = callback.data.replace("reassignser_", "").split("_to_")
    await reassign_server_owner_func(callback, server_id, new_owner_id)
