from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards.settings import get_back_to_settings_kb
from outboxes.settings import set_namecheap_api_key, set_namecheap_api_user, settings_handler_outbox_callback

class SetCredentialsState(StatesGroup):
    api_key = State()
    api_user = State()

router = Router()

@router.callback_query(F.data.startswith("settings"))
async def settings_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await settings_handler_outbox_callback(callback)

@router.callback_query(F.data.startswith("set_namecheap_api_key"))
async def set_namecheap_api_key_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Пожалуйста, отправьте ваш Namecheap API Key:", 
                                  reply_markup=await get_back_to_settings_kb())
    await state.set_state(SetCredentialsState.api_key)
    await callback.answer()

@router.message(StateFilter(SetCredentialsState.api_key))
async def receive_namecheap_api_key(message: Message, state: FSMContext):
    api_key = message.text.strip()
    await set_namecheap_api_key(message, api_key)
    await state.clear()

@router.callback_query(F.data.startswith("set_namecheap_api_user"))
async def set_namecheap_api_user_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text="Пожалуйста, отправьте ваш Namecheap API User:", 
                                  reply_markup=await get_back_to_settings_kb())
    await state.set_state(SetCredentialsState.api_user)
    await callback.answer()

@router.message(StateFilter(SetCredentialsState.api_user))
async def receive_namecheap_api_user(message: Message, state: FSMContext):
    api_user = message.text.strip()
    await set_namecheap_api_user(message, api_user)