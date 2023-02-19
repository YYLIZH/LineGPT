import os
from api.utils.configs import LANGUAGE


class Warning:
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        if LANGUAGE == "en":
            return f"Warning: {self.msg}"
        return f"警告: {self.msg}"


class Error:
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __str__(self) -> str:
        if LANGUAGE == "en":
            return f"Error: {self.msg}"
        return f"錯誤: {self.msg}"
