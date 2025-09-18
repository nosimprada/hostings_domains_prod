from aiogram.types import Message, CallbackQuery

from api import dynadot
from api.namecheap import get_user_balance
from config import CLIENT_IP
from keyboards.settings import (
    get_settings_dynadot_kb,
    get_settings_main_kb, 
    get_settings_namecheap_kb
)
from utils.database.services.user import get_namecheap_credentials, get_user_by_tg_id, update_dynadot_credentials, update_namecheap_credentials, update_namecheap_enabled
from utils.schemas.user_db import DynadotDataSchema, NamecheapDataSchema

async def settings_handler_outbox_func(callback: CallbackQuery):
    await callback.message.answer(text="Выберите провайдера для настройки:", 
                                  reply_markup=await get_settings_main_kb(callback.from_user.id))

async def settings_handler_namecheap_outbox_callback(callback: CallbackQuery):
    namecheap_credentials = await get_namecheap_credentials(callback.from_user.id)
    api_user = namecheap_credentials.api_user
    api_key = namecheap_credentials.api_key
    api_username = api_user  
    api_client_ip = CLIENT_IP
    status_namecheap = await get_user_balance(api_user=api_user, 
                                              api_key=api_key, 
                                              api_username=api_username, 
                                              api_client_ip=api_client_ip)
    if status_namecheap is not None:
        if namecheap_credentials.namecheap_enabled is False:
            await update_namecheap_enabled(namecheap_credentials.user_id, True)
    else:
        if namecheap_credentials.namecheap_enabled is True:
            await update_namecheap_enabled(namecheap_credentials.user_id, False)
    
    namecheap_credentials = await get_namecheap_credentials(callback.from_user.id)
    
    if namecheap_credentials and namecheap_credentials.namecheap_enabled:
        msg_info = f"""
==============================
🌐 <b>PROVIDER: Namecheap</b> (Активен) ✅

🛜 <b>IP: <code>{CLIENT_IP}</code></b>

🗝️ <b>Креденшелы:</b>
<b>┣ 👤 Логин: <code>{namecheap_credentials.api_user}</code></b>
<b>┗ 🔑 API ключ: <code>{namecheap_credentials.api_key}</code></b>
==============================
"""
    else:
        login = namecheap_credentials.api_user if namecheap_credentials.api_user else "—"
        api_key = namecheap_credentials.api_key if namecheap_credentials.api_key else "—"
        msg_info = f"""
==============================
🌐 <b>PROVIDER: Namecheap (Неактивен) ❌</b>
⚠️ Система Namecheap отключена или не настроена.
Пожалуйста, проверьте данные.

🔒 Убедитесь, что IP-адрес сервера добавлен 
в белый список в настройках безопасности вашего аккаунта Namecheap.
🛜 <b>IP: <code>{CLIENT_IP}</code></b>

🗝️ <b>Креденшелы:</b>
<b>┣ 👤 Логин: <code>{login}</code></b>
<b>┗ 🔑 API ключ: <code>{api_key}</code></b>
==============================
"""

    await callback.message.answer(text=msg_info, reply_markup=await get_settings_namecheap_kb())

async def settings_handler_namecheap_outbox_message(message: Message):
    namecheap_credentials = await get_namecheap_credentials(message.from_user.id)
    api_user = namecheap_credentials.api_user
    api_key = namecheap_credentials.api_key
    api_username = api_user  
    api_client_ip = CLIENT_IP
    status_namecheap = await get_user_balance(api_user=api_user, 
                                              api_key=api_key, 
                                              api_username=api_username, 
                                              api_client_ip=api_client_ip)
    if status_namecheap is not None:
        if namecheap_credentials.namecheap_enabled is False:
            await update_namecheap_enabled(namecheap_credentials.user_id, True)
    else:
        if namecheap_credentials.namecheap_enabled is True:
            await update_namecheap_enabled(namecheap_credentials.user_id, False)
    
    namecheap_credentials = await get_namecheap_credentials(message.from_user.id)
    if namecheap_credentials and namecheap_credentials.namecheap_enabled:
        msg_info = f"""
==============================
🌐 <b>PROVIDER: Namecheap</b> (Активен) ✅

🛜 <b>IP: <code>{CLIENT_IP}</code></b>

🗝️ <b>Креденшелы:</b>
<b>┣ 👤 Логин: <code>{namecheap_credentials.api_user}</code></b>
<b>┗ 🔑 API ключ: <code>{namecheap_credentials.api_key}</code></b>
==============================
"""
    else:
        login = namecheap_credentials.api_user if namecheap_credentials.api_user else "—"
        api_key = namecheap_credentials.api_key if namecheap_credentials.api_key else "—"
        msg_info = f"""
==============================
🌐 <b>PROVIDER: Namecheap (Неактивен) ❌</b>
⚠️ Система Namecheap отключена или не настроена.
Пожалуйста, проверьте данные.

🔒 Убедитесь, что IP-адрес сервера добавлен 
в белый список в настройках безопасности вашего аккаунта Namecheap.
🛜 <b>IP: <code>{CLIENT_IP}</code></b>

🗝️ <b>Креденшелы:</b>
<b>┣ 👤 Логин: <code>{login}</code></b>
<b>┗ 🔑 API ключ: <code>{api_key}</code></b>
==============================
"""

    await message.answer(text=msg_info, reply_markup=await get_settings_namecheap_kb())


async def set_namecheap_api_key(message: Message, api_key: str):
    namecheap_data = NamecheapDataSchema(
        user_id=message.from_user.id,
        api_key=api_key
    )
    await update_namecheap_credentials(namecheap_data)
    await settings_handler_namecheap_outbox_message(message)

async def set_namecheap_api_user(message: Message, api_user: str):
    namecheap_data = NamecheapDataSchema(
        user_id=message.from_user.id,
        api_user=api_user
    )
    await update_namecheap_credentials(namecheap_data)
    await settings_handler_namecheap_outbox_message(message)


async def settings_handler_dynadot_outbox_callback(callback: CallbackQuery):
    user_data = await get_user_by_tg_id(callback.from_user.id)
    dynadot_api_key = user_data.dynadot_api_key
    status_dynadot = await dynadot.get_user_balance(api_key=dynadot_api_key)
    print(status_dynadot)
    if status_dynadot is not None:
        msg_info = f"""
==============================
🌐 <b>PROVIDER: Dynadot</b> (Активен) ✅
🗝️ <b>Креденшелы:</b>
<b>┗ 🔑 API ключ: <code>{dynadot_api_key}</code></b>
==============================
"""
    else:
        api_key = dynadot_api_key if dynadot_api_key else "—"
        msg_info = f"""
==============================
🌐 <b>PROVIDER: Dynadot (Неактивен) ❌</b>
⚠️ Система Dynadot отключена или не настроена.
Пожалуйста, проверьте данные.

🔒 Убедитесь, что IP-адрес сервера добавлен
в белый список в настройках безопасности вашего аккаунта Dynadot.
🛜 <b>IP: <code>{CLIENT_IP}</code></b>

🗝️ <b>Креденшелы:</b>
<b>┗ 🔑 API ключ: <code>{api_key}</code></b>
==============================
"""
    await callback.message.answer(text=msg_info, reply_markup=await get_settings_dynadot_kb())

async def settings_handler_dynadot_outbox_message(message: Message):
    user_data = await get_user_by_tg_id(message.from_user.id)
    dynadot_api_key = user_data.dynadot_api_key
    status_dynadot = await dynadot.get_user_balance(api_key=dynadot_api_key)
    if status_dynadot is not None:
        msg_info = f"""
==============================
🌐 <b>PROVIDER: Dynadot</b> (Активен) ✅
🗝️ <b>Креденшелы:</b>
<b>┗ 🔑 API ключ: <code>{dynadot_api_key}</code></b>
==============================
"""
    else:
        api_key = dynadot_api_key if dynadot_api_key else "—"
        msg_info = f"""
==============================
🌐 <b>PROVIDER: Dynadot (Неактивен) ❌</b>
⚠️ Система Dynadot отключена или не настроена.
Пожалуйста, проверьте данные.

🔒 Убедитесь, что IP-адрес сервера добавлен
в белый список в настройках безопасности вашего аккаунта Dynadot.
🛜 <b>IP: <code>{CLIENT_IP}</code></b>

🗝️ <b>Креденшелы:</b>
<b>┗ 🔑 API ключ: <code>{api_key}</code></b>
==============================
"""
    await message.answer(text=msg_info, reply_markup=await get_settings_dynadot_kb())


async def set_dynadot_api_key_func(message: Message, api_key: str):
    await update_dynadot_credentials(DynadotDataSchema(
        user_id=message.from_user.id,
        dynadot_api_key=api_key
    ))
    await settings_handler_dynadot_outbox_message(message)