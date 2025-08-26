import re

def is_valid_uppercase(password):
    return bool(re.search(r'[A-Z]', password))