import typing
from abc import ABC

from api.utils.configs import LANGUAGE


class Command(ABC):
    usage_en = ""
    usage_zh = ""

    def __init__(
        self, subcommand: typing.Optional[str] = None, args: typing.Optional[str] = None
    ) -> None:
        self.args = args

    def execute(self, **kwargs):
        raise NotImplementedError

    def print_usage(cls):
        return getattr(cls, f"usage_{LANGUAGE}")
