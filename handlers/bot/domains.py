from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from keyboards.domains_kb import back_domains_kb, get_domains_menu_kb
from outboxes.domains import confirm_bind_domain_func, domains_menu, get_active_users_for_reassign_domain, \
    get_domain_management_menu, handle_action_auto_distribute_domains, handle_binding_domain_func, \
    handle_confirm_buy_domains_func, handle_domain_input_func, reassign_domain_handler_func

router = Router()


class DomainStates(StatesGroup):
    waiting_for_domains = State()
    confirm_buy_domains = State()
    waiting_action_by_domains = State()


@router.callback_query(F.data.startswith("domain_"))
async def handle_single_domain_query(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    domain_id = callback.data.split("_")[-1]
    await get_domain_management_menu(callback, domain_id)


@router.callback_query(F.data.startswith("domains_page_"))
async def handle_domains_pagination(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        page = int(callback.data.split("_")[-1])
    except ValueError:
        page = 1
    print("Запрошена страница в хендлере", page)  # Debugging line to check the requested page
    await domains_menu(callback, page=page)


@router.callback_query(F.data.startswith("admin_domains_page_"))
async def handle_admin_domains_pagination(callback: CallbackQuery):
    parts = callback.data.split("_")

    target_user_id = int(parts[3])
    page = int(parts[4])

    keyboard = await get_domains_menu_kb(target_user_id, page=page, admin=True)

    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("domains"))
async def handle_domains_query(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await domains_menu(callback)


@router.callback_query(F.data.startswith("create_domain"))
async def handle_create_domain_query(callback: CallbackQuery, state: FSMContext):
    msg = """
==============================
<b>🔎***Проверка доменов***🔍</b>

Отправьте каждый домен с новой строки.
==============================
Пример:
example.com
example.net
==============================
"""
    await state.set_state(DomainStates.waiting_for_domains)
    await callback.message.answer(text=msg, reply_markup=await back_domains_kb())


@router.message(StateFilter(DomainStates.waiting_for_domains))
async def handle_domain_input(message: Message, state: FSMContext):
    domains = message.text.strip().split("\n")
    domains = [domain.strip() for domain in domains if domain.strip()]
    if not domains:
        await message.answer("Пожалуйста, отправьте хотя бы один домен.")
        return
    print(domains)  # Debugging line to check the received domains
    await state.update_data(domains=domains)
    await handle_domain_input_func(message, state)
    await state.set_state(DomainStates.confirm_buy_domains)


@router.callback_query(StateFilter(DomainStates.confirm_buy_domains))
async def handle_confirm_buy_domains(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Начинаю обработку ваших доменов, это может занять некоторое время...')
    state_data = await state.get_data()
    domains = state_data.get("domains", [])
    if not domains:
        await callback.message.answer("Нет доступных доменов для покупки.")
        return
    await handle_confirm_buy_domains_func(callback, state)
    await state.set_state(DomainStates.waiting_action_by_domains)


@router.callback_query(StateFilter(DomainStates.waiting_action_by_domains))
async def handle_action_by_domains(callback: CallbackQuery, state: FSMContext):
    if callback.data.startswith("auto_distribute_domains"):
        await callback.message.answer('Начинаю автоматическое распределение доменов...')
        await handle_action_auto_distribute_domains(callback, state)


@router.callback_query(F.data.startswith("binding_"))
async def handle_binding_domain(callback: CallbackQuery):
    domain_id = callback.data.split("_")[-1]
    await handle_binding_domain_func(callback, domain_id)


@router.callback_query(F.data.startswith("bind_domain_"))
async def confirm_bind_domain(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) != 4:
        await callback.message.answer("Некорректные данные для привязки домена.")
        return
    await callback.message.answer('Привязываю домен к серверу, это может занять некоторое время...')
    domain_id = parts[2]
    server_id = parts[3]
    await confirm_bind_domain_func(callback, domain_id, server_id)


@router.callback_query(F.data.startswith("reassign_owner_"))
async def handle_reassign_owner(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) != 3:
        await callback.message.answer("Некорректные данные для переназначения владельца.")
        return
    domain_id = parts[2]
    await get_active_users_for_reassign_domain(callback, domain_id)


@router.callback_query(F.data.startswith("reassign_"))
async def reassign_domain_handler(callback: CallbackQuery):
    # callback.data: 'reassign_{domain_id}_to_{user_id}'
    parts = callback.data.split("_")
    domain_id = parts[1]
    user_id = parts[3]
    await reassign_domain_handler_func(callback, domain_id, user_id)
