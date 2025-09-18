from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.settings import (
    get_back_to_dynadot_settings_kb, 
    get_back_to_namecheap_settings_kb
)
from outboxes.settings import (
    set_dynadot_api_key_func,
    set_namecheap_api_key, 
    set_namecheap_api_user,
    settings_handler_dynadot_outbox_callback,
    settings_handler_namecheap_outbox_callback, 
    settings_handler_outbox_func
)

class SetCredentialsNamecheapState(StatesGroup):
    api_key = State()
    api_user = State()

class SetCredentialsDynadotState(StatesGroup):
    api_key = State()

router = Router()


@router.callback_query(F.data == "settings")
async def settings_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await settings_handler_outbox_func(callback)


@router.callback_query(F.data.startswith("settings_namecheap"))
async def settings_namecheap_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await settings_handler_namecheap_outbox_callback(callback)




@router.callback_query(F.data.startswith("set_namecheap_api_key"))
async def set_namecheap_api_key_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Пожалуйста, отправьте ваш Namecheap API Key:", 
                                  reply_markup=await get_back_to_namecheap_settings_kb())
    await state.set_state(SetCredentialsNamecheapState.api_key)
    await callback.answer()

@router.message(StateFilter(SetCredentialsNamecheapState.api_key))
async def receive_namecheap_api_key(message: Message, state: FSMContext):
    api_key = message.text.strip()
    await set_namecheap_api_key(message, api_key)
    await state.clear()

@router.callback_query(F.data.startswith("set_namecheap_api_user"))
async def set_namecheap_api_user_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Пожалуйста, отправьте ваш Namecheap API User:", 
                                  reply_markup=await get_back_to_namecheap_settings_kb())
    await state.set_state(SetCredentialsNamecheapState.api_user)
    await callback.answer()

@router.message(StateFilter(SetCredentialsNamecheapState.api_user))
async def receive_namecheap_api_user(message: Message, state: FSMContext):
    api_user = message.text.strip()
    await set_namecheap_api_user(message, api_user)

@router.callback_query(F.data.startswith("settings_dynadot"))
async def settings_dynadot_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await settings_handler_dynadot_outbox_callback(callback)


@router.callback_query(F.data.startswith("set_dynadot_api_key"))
async def set_dynadot_api_key_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Пожалуйста, отправьте ваш Dynadot API Key:", 
                                  reply_markup=await get_back_to_dynadot_settings_kb())
    await state.set_state(SetCredentialsDynadotState.api_key)
    await callback.answer()

@router.message(StateFilter(SetCredentialsDynadotState.api_key))
async def receive_dynadot_api_key(message: Message, state: FSMContext):
    api_key = message.text.strip()
    await set_dynadot_api_key_func(message, api_key)
    await state.clear()