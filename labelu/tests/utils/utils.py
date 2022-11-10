import random
import string
from typing import Dict


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=16))


def random_username() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"
