import re


def snake_case(camelCase):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camelCase).lower()


def complete_dict(a, b):
    keys = set(b.keys())
    for key in keys:
        if not a.get(key) and b.get(key):
            a[key] = b[key]
    return a
