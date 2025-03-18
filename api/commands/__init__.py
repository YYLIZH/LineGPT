from collections import namedtuple
from typing import Dict
from api.utils.configs import LANGUAGE

CommandInfo = namedtuple(
    "CommandInfo",
    "module_path, class_name, summary_en, summary_zh_TW",
)
commands_info: Dict[str, CommandInfo] = {
    "gpt": CommandInfo(
        "api.commands.gpt", "GptCommand", "GPT commands", "GPT 指令"
    ),
    "weather": CommandInfo(
        "api.commands.weather",
        "WeatherCommand",
        "Check the weather",
        "查看天氣",
    ),
    "settle": CommandInfo(
        "api.commands.settle",
        "SettleCommand",
        "Settle the expenses among a group",
        "多人分帳",
    ),
    "eat": CommandInfo(
        "api.commands.eat",
        "EatCommand",
        "What to eat now",
        "現在吃什麼",
    ),
}


def print_usage():
    heading = (
        "嗨！我是LineGPT，很高興為您服務。以下是我的使用說明：\n\n"
        "@LineGPT <指令>\n"
        "可用指令\n"
    )
    footer = "\n您可以使用'@LineGPT <指令> help'來查看更多資訊"
    if LANGUAGE == "en":
        heading = (
            "Hi! I am LineGPT. It's my pleasure to help you. Here is the usage:\n\n"
            "@LineGPT <Command>\n"
            "Available commands\n"
        )
        footer = "\nYou can use '@LineGPT <Command> help' to get more information about each command."

    res = heading
    for key, value in commands_info.items():
        summary = getattr(value, f"summary_{LANGUAGE}")
        line = f"{key:<15}{summary}\n"
        res += line
    res += footer
    return res
