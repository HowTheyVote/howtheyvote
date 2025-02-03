from collections.abc import Callable


def one_of(*args: str) -> Callable[[str], str]:
    """Returns a function that validates if a given value is one of the provided
    values and returns a `ValueError` otherwise."""

    def convert(value: str) -> str:
        if value in args:
            return value
        raise ValueError(f"Invalid value {value}")

    return convert
