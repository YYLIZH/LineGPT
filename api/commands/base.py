import typing
from abc import ABC

from api.utils.configs import LANGUAGE


class Command(ABC):
    usage_en = ""
    usage_zh_TW = ""

    def __init__(
        self, subcommand: typing.Optional[str] = None, args: typing.Optional[str] = None
    ) -> None:
        self.subcommand = subcommand.strip() if subcommand else None
        self.args = args.strip() if args else None

    @classmethod
    def print_usage(cls):
        return getattr(cls, f"usage_{LANGUAGE}")

    @classmethod
    def setup(cls, args_msg: str):
        raise NotImplementedError

    def execute(self, **kwargs):
        raise NotImplementedError
