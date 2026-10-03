import re

def validate_email(email):
    """Validates email format."""
    if not email or not isinstance(email, str):
        return False
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def normalize_email(email):
    """Normalizes the email to lowercase and strips whitespace."""
    if email and isinstance(email, str):
        return email.strip().lower()
    return email

def validate_password(password):
    """
    Validates password strength.
    Requires at least 8 characters.
    """
    if not password or not isinstance(password, str):
        return False
    return len(password) >= 8

def validate_name(name):
    """Validates that a name is provided and reasonable length."""
    if not name or not isinstance(name, str):
        return False
    name = name.strip()
    return 2 <= len(name) <= 100

def validate_price(price):
    if price is None or not isinstance(price, (int, float)):
        return False
    return price >= 0

def validate_sizes(sizes):
    if not isinstance(sizes, list):
        return False
    if not sizes:
        return False
    for size in sizes:
        if not isinstance(size, str) or not size.strip():
            return False
    return True

