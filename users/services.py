import secrets
import string


def get_password(password_len=12):

    # Создание двенадцатисимвольного (по умолчанию) буквенно-цифрового пароля,
    # содержащего как минимум один символ нижнего регистра,
    # как минимум один символ верхнего регистра и как минимум три цифры:
    alphabet = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphabet) for i in range(password_len))
        if not any(c.islower() for c in password) or not any(c.isupper() for c in password) or sum(
                c.isdigit() for c in password) < 3:
            continue
        break

    return password
