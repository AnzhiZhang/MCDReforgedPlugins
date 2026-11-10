__all__ = [
    "MissingRequiredAttribute",
]


class MissingRequiredAttribute(Exception):
    def __init__(self, name: str):
        super().__init__(f"Missing required attribute \"{name}\"")
