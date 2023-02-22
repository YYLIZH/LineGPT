"""Configs loader.

Parse and load env configs in this module.
All modules should import env setting from this module.

"""
import os
from functools import cache
from typing import Tuple

from dotenv import load_dotenv

load_dotenv()
environ = os.environ


def _parse_necessary(key: str) -> str:
    value = environ.get(key)
    if value is None or value == "":
        raise ValueError(f"{key} must be set in .env file.")
    return value


@cache
def parse_main():
    lang = environ.get("LANGUAGE")
    sesssion_expired = environ.get("SESSION_EXPIRE")
    if lang not in ["zh", "en"]:
        lang = "zh"
    return lang, sesssion_expired


@cache
def parse_line():
    channel_secret = _parse_necessary("LINE_CHANNEL_SECRET")
    channel_access_token = _parse_necessary("LINE_CHANNEL_ACCESS_TOKEN")
    return channel_secret, channel_access_token


@cache
def parse_openai() -> Tuple[str, str, float, int, float, float]:
    check_table = {
        "text-davinci-003": 4096,
        "text-curie-001": 2048,
        "text-babbage-001": 2048,
        "text-ada-001": 2048,
    }
    model = environ.get("OPENAI_MODEL")
    if not model in check_table.keys():
        raise ValueError(f"{model} is not in allowable models.")

    api_key = _parse_necessary("OPENAI_API_KEY")

    temperature = float(environ.get("OPENAI_TEMPERATURE"))
    if not 0.0 <= temperature <= 2.0:
        temperature = 0.9

    max_token = int(environ.get("OPENAI_MAX_TOKEN"))
    if max_token > check_table[model]:
        max_token = 240

    presence_penalty = float(environ.get("OPENAI_PRESENCE_PENALTY"))
    if not -2.0 <= presence_penalty <= 2.0:
        presence_penalty = 0.0

    frequency_penalty = float(environ.get("OPENAI_FREQUENCY_PENALTY"))
    if not -2.0 <= frequency_penalty <= 2.0:
        frequency_penalty = 0.0

    return model, api_key, temperature, max_token, presence_penalty, frequency_penalty


@cache
def parse_open_data() -> str:
    weather_token = environ.get("WEATHER_TOKEN")
    if weather_token:
        return weather_token
    return "NODATA"


LANGUAGE, SESSION_EXPIRED = parse_main()
LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN = parse_line()
(
    OPENAI_MODEL,
    OPENAI_API_KEY,
    OPENAI_TEMPERATURE,
    OPENAI_MAX_TOKEN,
    OPENAI_PRESENCE_PENALTY,
    OPENAI_FREQUENCY_PENALTY,
) = parse_openai()
WEATHER_TOKEN = parse_open_data()
