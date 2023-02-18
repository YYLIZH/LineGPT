import os

language = os.getenv("LANGUAGE", default="zh")


class Warning:
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        return f"Warning: {self.msg}"
