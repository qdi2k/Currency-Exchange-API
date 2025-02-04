def password_validator(value: str):
    """Валидация пароля"""
    if len(value) < 8:
        raise ValueError("Пароль должен быть более 8 символов")
    if not any(c.isupper() for c in value):
        raise ValueError("Пароль должен содержать минимум 1 символ"
                         + " верхнего регистра")
    if not any(c.islower() for c in value):
        raise ValueError("Пароль должен содержать минимум 1 символ"
                         + " нижнего регистра")
    if not any(c.isdigit() for c in value):
        raise ValueError("Пароль должен содержать минимум 1 цифру")

    return value
