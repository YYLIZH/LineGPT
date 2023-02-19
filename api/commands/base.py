from abc import ABC, abstractmethod
from api.utils.configs import LANGUAGE


class Command(ABC):
    def __init__(self, args: str) -> None:
        self.args = args

    @staticmethod
    def help_en():
        pass

    @staticmethod
    def help_zh():
        pass

    def execute(self):
        raise NotImplementedError

    @classmethod
    def print_help(cls):
        return getattr(cls, f"help_{LANGUAGE}")()
