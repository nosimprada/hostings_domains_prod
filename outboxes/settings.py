from aiogram.types import Message, CallbackQuery

from api.namecheap import get_user_balance
from config import CLIENT_IP
from keyboards.settings import get_settings_namecheap_kb
from utils.database.services.user import get_namecheap_credentials, update_namecheap_credentials, update_namecheap_enabled
from utils.schemas.user_db import NamecheapDataSchema

async def settings_handler_outbox_callback(callback: CallbackQuery):
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

async def settings_handler_outbox_message(message: Message):
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
    await settings_handler_outbox_message(message)

async def set_namecheap_api_user(message: Message, api_user: str):
    namecheap_data = NamecheapDataSchema(
        user_id=message.from_user.id,
        api_user=api_user
    )
    await update_namecheap_credentials(namecheap_data)
    await settings_handler_outbox_message(message)