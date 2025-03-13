"""Configs loader.

Parse and load env configs in this module.
All modules should import env setting from this module.

"""

import os
import typing
from functools import cache

from dotenv import load_dotenv

load_dotenv()
environ = os.environ


def _parse_necessary(key: str) -> str:
    value = environ.get(key)
    if value is None or value == "":
        raise ValueError(f"{key} must be set in .env file.")
    return value


@cache
def parse_language() -> typing.Literal["en", "zh_TW"]:
    available_lang = ["en", "zh_TW"]

    lang = environ.get("LANGUAGE")
    if lang not in available_lang:
        return "en"
    return lang


@cache
def parse_line() -> typing.Tuple[str, str]:
    channel_secret = _parse_necessary("LINE_CHANNEL_SECRET")
    channel_access_token = _parse_necessary(
        "LINE_CHANNEL_ACCESS_TOKEN"
    )
    return channel_secret, channel_access_token


@cache
def parse_session_expired() -> int:
    if environ.get("SESSION_EXPIRE"):
        return int(environ["SESSION_EXPIRE"])
    return 600


@cache
def parse_weather_token() -> str:
    default_weather_token = "CWB-D4A3A110-A4B2-4A2F-AEB2-321F489C3383"
    return environ.get("WEATHER_TOKEN") or default_weather_token


@cache
def parse_google_api_key() -> str:
    if environ.get("GOOGLE_API_KEY"):
        return environ["GOOGLE_API_KEY"]
    return ""


LANGUAGE = parse_language()
LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN = parse_line()
SESSION_EXPIRED = parse_session_expired()
WEATHER_TOKEN = parse_weather_token()
GOOGLE_API_KEY = parse_google_api_key()
