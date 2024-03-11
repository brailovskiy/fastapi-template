from typing import Any


def to_upper(string: str | Any) -> str:
    if isinstance(string, str):
        return string.upper()
    return string
