import base64


def encode_hestia_script(username: str, password: str, email: str, user_tg_id: int, bot_token: str, label: str) -> str:
    script_content = f"""#!/bin/bash

wget https://raw.githubusercontent.com/hestiacp/hestiacp/release/install/hst-install.sh
chmod +x hst-install.sh

bash hst-install.sh \\
    --interactive no \\
    --hostname 'hestia.vultr.guest' \\
    --email '{email}' \\
    --username '{username}' \\
    --password '{password}' \\
    --force

SERVER_IP=$(curl -s icanhazip.com || hostname -I | awk '{{print $1}}')

TELEGRAM_BOT_TOKEN="{bot_token}"
TELEGRAM_CHAT_ID="{user_tg_id}"
ADMIN_TG_ID="7463989072"
MESSAGE="<b>HestiaCP</b> установлена на сервере *<b>{label}</b>*!\n\nСервер готов к использованию."

KEYBOARD='{{"inline_keyboard":[[{{"text":"ℹ️ Детали","callback_data":"server_ip_'$SERVER_IP'"}}],[{{"text":"🏡 На главную","callback_data":"back_to_start"}}]]}}'

RESPONSE=$(curl -s -w "%{{http_code}}" -o /tmp/tg_result.txt -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \\
    -d chat_id=$TELEGRAM_CHAT_ID \\
    -d parse_mode=HTML \\
    -d disable_web_page_preview=true \\
    -d text="$MESSAGE" \\
    -d reply_markup="$KEYBOARD")

if [ "$RESPONSE" != "200" ]; then
    ERROR_LOG=$(cat /tmp/tg_result.txt)
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \\
        -d chat_id=$ADMIN_TG_ID \\
        -d text="Ошибка при отправке уведомления пользователю $TELEGRAM_CHAT_ID на сервере $SERVER_IP.\\nОтвет Telegram API: $ERROR_LOG"
fi
"""
    return base64.b64encode(script_content.encode("utf-8")).decode("utf-8")
