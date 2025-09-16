import random
import string

def generate_password(length: int = 14) -> str:
    if length < 8:
        raise ValueError("Пароль должен быть не менее 8 символов")

    chars = string.ascii_letters + string.digits
    while True:
        password = ''.join(random.choice(chars) for _ in range(length))
        if (any(c.isdigit() for c in password) and
            any(c.islower() for c in password) and
            any(c.isupper() for c in password)):
            return password