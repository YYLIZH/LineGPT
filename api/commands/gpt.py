import re
import textwrap
from datetime import datetime, timedelta
from enum import Enum

import g4f
from jinja2 import Template

from api.utils.configs import LANGUAGE, SESSION_EXPIRED
from api.utils.info import Error, Warning


class MessageEN(str, Enum):
    GREETING = "Start the dialogue session."
    FOUND_SESSION = "Found existing session. You can see existing session's dialog, keep talking, or restart a new session."
    NO_SESSION = (
        "Session does not exist. Please start the session first."
    )
    SESSION_EXPIRED = "Current dialogue session is expired. Please restart the dialogue session."
    RUNTIME_ERROR = "RuntimeError. Please ask again later."
    UNEXPECTED_ERROR = (
        "Unexpected error happened. Restart the session."
    )
    CLOSE = "Close current dialogue session."
    RESTART = "Restart the dialogue session"
    LOG = "Below are the past dialogues:"
    NOT_ALLOW_METHOD = "This method is not allowed."


class MessageZHTW(str, Enum):
    GREETING = "對話階段已開始"
    FOUND_SESSION = "存在舊有的對話階段，您可以查看紀錄、繼續對話、或是重啟對話階段。"
    NO_SESSION = (
        '尚未開啟對話階段，請先使用"@LineGPT start"開啟對話。'
    )
    SESSION_EXPIRED = '當前對話階段已過期。請先使用"@LineGPT restart"重新開啟對話階段。'
    RUNTIME_ERROR = "RuntimeError. 請稍後再試一次"
    UNEXPECTED_ERROR = "發生未知的錯誤，重啟對話。"
    CLOSE = "關閉對話階段。"
    RESTART = "重新啟動對話階段"
    LOG = "以下是對話紀錄："
    NOT_ALLOW_METHOD = "不存在的指令"


MESSAGE = MessageZHTW if LANGUAGE == "zh_TW" else MessageEN


LOG_TEMPLATE: Template = Template(
    textwrap.dedent(
        """
    {% for message in log %}
    {{ "{:>10}".format(message.role) }}: {{message.content}}
    {% endfor %}
    """
    ),
    trim_blocks=True,
)


class DialogueSession:
    def __init__(self) -> None:
        spoken_lang = "English"
        if LANGUAGE == "zh_TW":
            spoken_lang = "繁體中文"
        self.dialogue = [
            {
                "role": "system",
                "content": f"You are a helpful assistant. Please respond in {spoken_lang}.",
            }
        ]

        self.client = g4f.client.Client()
        self.last_update_time = datetime.now()

    @property
    def is_expired(self) -> bool:
        time_delta: timedelta = datetime.now() - self.last_update_time
        if time_delta.total_seconds() >= int(SESSION_EXPIRED):
            return True
        return False

    def talk(self, text: str) -> str:
        if self.is_expired:
            return str(Warning(MESSAGE.SESSION_EXPIRED.value))

        self._add_human_text(text)
        try:
            raw_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.dialogue,
            )
        except Exception:
            self.dialogue.pop()
            return str(Error(MESSAGE.RUNTIME_ERROR.value))

        ai_response = raw_response.choices[0].message.content.strip()
        self._add_ai_text(text=ai_response)
        return ai_response

    def _add_ai_text(self, text: str) -> None:
        self.dialogue.append({"role": "assistant", "content": text})
        self.last_update_time = datetime.now()

    def _add_human_text(self, text: str) -> None:
        self.dialogue.append({"role": "user", "content": text})
        self.last_update_time = datetime.now()


class GPT:
    def __init__(self) -> None:
        self.dialogue_session: DialogueSession | None = None

    def start(self) -> str:
        """Start a GPT dialogue session"""
        if self.dialogue_session is not None:
            return MESSAGE.FOUND_SESSION.value

        self.dialogue_session = DialogueSession()
        return MESSAGE.GREETING.value

    def close(self) -> str:
        """Close a dialogue session"""
        self.dialogue_session = None
        return MESSAGE.CLOSE.value

    def restart(self) -> str:
        """Close an old dialogue session and start a new one"""
        self.dialogue_session = DialogueSession()
        return MESSAGE.RESTART.value

    def talk(self, text: str) -> str:
        if self.dialogue_session is None:
            return str(Warning(MESSAGE.NO_SESSION.value))

        try:
            return self.dialogue_session.talk(text)
        except Exception:
            return str(Error(MESSAGE.UNEXPECTED_ERROR.value))

    def log(self) -> str:
        if isinstance(self.dialogue_session, DialogueSession):
            return (
                MESSAGE.LOG.value
                + "\n"
                + LOG_TEMPLATE.render(
                    {"log": self.dialogue_session.dialogue}
                )
            )
        return str(Warning(MESSAGE.NO_SESSION.value))


gpt = GPT()


def print_help() -> str:
    usage_en = textwrap.dedent(
        """
        * Start a dialogue session.
        @LineGPT gpt start

        * Show dialogue
        @LineGPT gpt log

        * Ask a question
        @LineGPT gpt talk <your question> 

        Example:
        @LineGPT gpt talk What is graphene?

        * Close an existing dialogue session
        @LineGPT gpt close

        * Restart a dialogue session
        @LineGPT gpt restart
        """
    )

    usage_zh_TW = textwrap.dedent(
        """
        * 開始對話階段
        @LineGPT gpt start

        * 顯示過往對話紀錄
        @LineGPT gpt log

        * 提問
        @LineGPT gpt talk <your question> 

        Example:
        @LineGPT gpt talk 請告訴我怎麼變有錢人

        * 關閉對話階段，過往紀錄將會被刪除
        @LineGPT gpt close

        * 重新開始對話階段
        @LineGPT gpt restart
        """
    )
    if LANGUAGE == "zh_TW":
        return usage_zh_TW
    return usage_en


def handle_message(message: str) -> str:
    if mrx := re.search(r"gpt\s+(\w+)\s*(.*)", message):
        match mrx.group(1):
            case "start":
                return gpt.start()

            case "log":
                return gpt.log()

            case "talk":
                if mrx.group(2):
                    return gpt.talk(mrx.group(2))
                return "@LineGPT gpt talk <your question>"

            case "close":
                return gpt.close()

            case "restart":
                return gpt.restart()

            case _:
                return MESSAGE.NOT_ALLOW_METHOD.value

    return print_help()
