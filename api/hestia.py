from asyncssh import connect

HESTIA_BIN_PATH = "/usr/local/hestia/bin"


async def add_domain(ssh_ip: str, ssh_password: str, hestia_username: str, domain: str) -> bool | ValueError:
    try:
        domain = domain.lower()
        async with connect(host=ssh_ip, username="root", password=ssh_password, known_hosts=None) as conn:
            result = await conn.run(f"{_hestia_bin_path('v-add-domain')} {hestia_username} {domain} {ssh_ip}")

            # Если 0 - вернется True, если 1 - вернется ValueError с сообщением об ошибке
            return True if result.exit_status == 0 else ValueError(result.stderr)
    except Exception as e:
        print(f"Error: {str(e)}")


async def enable_ssl_for_domain(ssh_ip: str, ssh_password: str, hestia_username: str, domain: str) -> bool | ValueError:
    try:
        async with connect(host=ssh_ip, username="root", password=ssh_password, known_hosts=None) as conn:
            result = await conn.run(f"""
                        {_hestia_bin_path("v-add-letsencrypt-domain")} {hestia_username} {domain} www.{domain} &&
                        {_hestia_bin_path("v-add-web-domain-ssl-force")} {hestia_username} {domain}
                        """)

            # Если 0 - вернется True, если 1 - вернется ValueError с сообщением об ошибке
            return True if result.exit_status == 0 else ValueError(result.stderr)
    except Exception as e:
        print(f"Error: {str(e)}")


async def change_user_password(ssh_ip: str, ssh_password: str, hestia_username: str, new_password: str
                               ) -> bool | ValueError:
    try:
        async with connect(host=ssh_ip, username="root", password=ssh_password, known_hosts=None) as conn:
            result = await conn.run(f"""
                        {_hestia_bin_path("v-change-user-password")} {hestia_username} {new_password}
                        """)

            # Если 0 - вернется True, если 1 - вернется ValueError с сообщением об ошибке
            return True if result.exit_status == 0 else ValueError(result.stderr)
    except Exception as e:
        print(f"Error: {str(e)}")


def _hestia_bin_path(s: str) -> str:
    return f"{HESTIA_BIN_PATH}/{s}"
