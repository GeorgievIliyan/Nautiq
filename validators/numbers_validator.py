def is_valid_number(password):
    for char in password:
        if char.isdigit():
            return True
    return False