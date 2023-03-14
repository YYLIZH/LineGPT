"""Configs loader.

Parse and load env configs in this module.
All modules should import env setting from this module.

"""
import os
from functools import cache
from typing import Tuple
from enum import Enum
from dotenv import load_dotenv

load_dotenv()
environ = os.environ


class LANGUAGE_Enum(Enum):
    English = "en"
    Tranditional_Chinese = "zh_TW"

    @classmethod
    def available(cls):
        return [member.value for _, member in cls.__members__.items()]


class OPENAI_MODEL_Enum(Enum):
    gpt = "gpt-3.5-turbo"
    davinci = "text-davinci-003"

    @classmethod
    def available(cls):
        return [member.value for _, member in cls.__members__.items()]


class Default(Enum):
    LANGUAGE = LANGUAGE_Enum.Tranditional_Chinese
    OPENAI_API_KEY = None
    OPENAI_MODEL = OPENAI_MODEL_Enum.gpt
    OPENAI_TEMPERATURE = 0.9
    OPENAI_MAX_TOKEN = 150
    OPENAI_PRESENCE_PENALTY = 0.6
    OPEN_FREQUENCY_PENALTY = 0.0
    SESSION_EXPIRE = 600
    WEATHER_TOKEN = "CWB-D4A3A110-A4B2-4A2F-AEB2-321F489C3383"


def _parse_necessary(key: str) -> str:
    value = environ.get(key)
    if value is None or value == "":
        raise ValueError(f"{key} must be set in .env file.")
    return value


@cache
def parse_main() -> str:
    lang = environ.get("LANGUAGE")
    if lang not in LANGUAGE_Enum.available():
        return Default.LANGUAGE
    return lang


@cache
def parse_line():
    channel_secret = _parse_necessary("LINE_CHANNEL_SECRET")
    channel_access_token = _parse_necessary("LINE_CHANNEL_ACCESS_TOKEN")
    return channel_secret, channel_access_token


@cache
def parse_openai() -> Tuple[str, str, float, int, float, float, int]:
    model_token = {
        "gpt-3.5-turbo": 4096,
        "text-davinci-003": 4097,
    }
    model = environ.get("OPENAI_MODEL")
    if not model:
        model = Default.OPENAI_MODEL

    elif model not in OPENAI_MODEL_Enum.available():
        raise ValueError(f"{model} is not in allowable models.")

    api_key = environ.get("OPENAI_API_KEY")

    temperature = float(environ.get("OPENAI_TEMPERATURE"))
    if not 0.0 <= temperature <= 2.0:
        temperature = Default.OPENAI_TEMPERATURE

    max_token = int(environ.get("OPENAI_MAX_TOKEN"))
    if max_token > model_token[model]:
        max_token = Default.OPENAI_MAX_TOKEN

    presence_penalty = float(environ.get("OPENAI_PRESENCE_PENALTY"))
    if not -2.0 <= presence_penalty <= 2.0:
        presence_penalty = Default.OPENAI_PRESENCE_PENALTY

    frequency_penalty = float(environ.get("OPENAI_FREQUENCY_PENALTY"))
    if not -2.0 <= frequency_penalty <= 2.0:
        frequency_penalty = Default.OPEN_FREQUENCY_PENALTY

    session_expire = int(environ.get("SESSION_EXPIRE"))
    if not session_expire:
        session_expire = Default.SESSION_EXPIRE

    return (
        model,
        api_key,
        temperature,
        max_token,
        presence_penalty,
        frequency_penalty,
        session_expire,
    )


@cache
def parse_open_data() -> str:
    return environ.get("WEATHER_TOKEN") or Default.WEATHER_TOKEN


LANGUAGE = parse_main()
LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN = parse_line()
(
    OPENAI_MODEL,
    OPENAI_API_KEY,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKEN,
    OPENAI_PRESENCE_PENALTY,
    OPENAI_FREQUENCY_PENALTY,
    SESSION_EXPIRED,
) = parse_openai()
WEATHER_TOKEN = parse_open_data()
