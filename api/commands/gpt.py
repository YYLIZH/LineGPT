from __future__ import annotations
import datetime
import re
import typing
from enum import Enum
from typing import Dict

import openai

from api.commands.base import Command
from api.utils.configs import (
    LANGUAGE,
    OPENAI_API_KEY,
    OPENAI_FREQUENCY_PENALTY,
    OPENAI_MAX_TOKEN,
    OPENAI_MODEL,
    OPENAI_PRESENCE_PENALTY,
    OPENAI_TEMPERATURE,
    SESSION_EXPIRED,
)
from api.utils.info import Error, Warning


class MessageEN(Enum):
    GREETING = "Start the dialogue session."
    FOUND_SESSION = "Found existing session. You can see existing session's dialog, keep talking, or restart a new session."
    NO_SESSION = "Session does not exist. Please start the session first."
    SESSION_EXPIRED = (
        "Current dialogue session is expired. Please restart the dialogue session."
    )
    RUNTIME_ERROR = "RuntimeError. Please ask again later."
    UNEXPECTED_ERROR = "Unexpected error happened. Restart the session."
    CLOSE = "Close current dialogue session."
    RESTART = "Restart the dialogue session"
    LOG = "Below are the past dialogues:"
    NOT_ALLOW_METHOD = "This method is not allowed."


class MessageZHTW(Enum):
    GREETING = "對話階段已開始"
    FOUND_SESSION = "存在舊有的對話階段，您可以查看紀錄、繼續對話、或是重啟對話階段。"
    NO_SESSION = '尚未開啟對話階段，請先使用"@LineGPT start"開啟對話。'
    SESSION_EXPIRED = '當前對話階段已過期。請先使用"@LineGPT restart"重新開啟對話階段。'
    RUNTIME_ERROR = "RuntimeError. 請稍後再試一次"
    UNEXPECTED_ERROR = "發生未知的錯誤，重啟對話。"
    CLOSE = "關閉對話階段。"
    RESTART = "重新啟動對話階段"
    LOG = "以下是對話紀錄："
    NOT_ALLOW_METHOD = "不存在的指令"


USAGE_EN = """* Start a dialogue session.
@LineGPT gpt start

* Show dialogue
@LineGPT gpt log

* Ask a question
@LineGPT gpt talk <your question> 
Example:
@LineGPT gpt talk What is graphene?

* Close an existing dialogue session
@LineGPT gpt close
"""

USAGE_ZH_TW = """* 開始對話階段
@LineGPT gpt start

* 顯示過往對話紀錄
@LineGPT gpt log

* 提問
@LineGPT gpt talk <your question> 
Example:
@LineGPT gpt talk 請告訴我怎麼變有錢人

* 關閉對話階段，過往紀錄將會被刪除
@LineGPT gpt close
"""

openai.api_key = OPENAI_API_KEY
MESSAGE = MessageEN if LANGUAGE == "en" else MessageZHTW


class DialogueSession:
    def __init__(self) -> None:
        self.dialogue = []
        self.last_update_time = datetime.datetime.now()

    def add_ai_text(self, text: str) -> None:
        self.dialogue.append(f"AI: {text}")
        self.last_update_time = datetime.datetime.now()

    def add_human_text(self, text: str) -> None:
        self.dialogue.append(f"Human: {text}")
        self.last_update_time = datetime.datetime.now()

    def dump_dialogue(self) -> str:
        return "\n".join(self.dialogue)

    def is_expired(self) -> bool:
        time_delta: datetime.timedelta = datetime.datetime.now() - self.last_update_time
        if time_delta.seconds >= int(SESSION_EXPIRED):
            return True
        return False


class GPT:
    def __init__(self) -> None:
        self.dialogue_session = DialogueSession()
        self.model = OPENAI_MODEL
        self.temperature = OPENAI_TEMPERATURE
        self.max_tokens = OPENAI_MAX_TOKEN
        self.frequency_penalty = OPENAI_FREQUENCY_PENALTY
        self.presence_penalty = OPENAI_PRESENCE_PENALTY

    def _talk(self):
        response = openai.Completion.create(
            model=self.model,
            prompt=self.dialogue_session.dump_dialogue(),
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
        )
        text = response["choices"][0]["text"].strip()
        extracted_text = re.search(r"(\w+: +)?([\s\S]*)", text).group(2)
        extracted_text = extracted_text.replace("AI: ", "")
        self.dialogue_session.add_ai_text(extracted_text)
        return extracted_text

    def talk(self, text):
        if self.dialogue_session is None:
            return Warning(MESSAGE.NO_SESSION.value)
        if self.dialogue_session.is_expired():
            return Warning(MESSAGE.SESSION_EXPIRED.value)

        self.dialogue_session.add_human_text(text)
        try:
            response = self._talk()
        except Exception:
            self.dialogue_session.dialogue.pop()
            return Error(MESSAGE.RUNTIME_ERROR.value)
        return response


class GPTSessions:
    def __init__(self) -> None:
        """Each Group use different gpt."""
        self.sessions: Dict[str, GPT] = {}

    def start(self, group_id: str) -> str:
        """Start a GPT and add into session."""
        if gpt := self.sessions.get(group_id):
            return MESSAGE.FOUND_SESSION.value
        gpt = GPT()
        self.sessions[group_id] = gpt
        return MESSAGE.GREETING.value

    def close(self, group_id: str) -> str:
        self.sessions.pop(group_id)
        return MESSAGE.CLOSE.value

    def restart(self, group_id: str) -> str:
        gpt = GPT()
        self.sessions[group_id] = gpt
        return MESSAGE.GREETING.value

    def talk(self, group_id: str, text: str) -> str:
        if not self.sessions.get(group_id):
            return Warning(MESSAGE.NO_SESSION.value)
        gpt = self.sessions.get(group_id)
        try:
            return gpt.talk(text)
        except Exception:
            self.sessions[group_id] = GPT()
            return Error(MESSAGE.UNEXPECTED_ERROR.value)

    def log(self, group_id: str) -> str:
        gpt = self.sessions.get(group_id)
        return MESSAGE.LOG.value + "\n" + gpt.dialogue_session.dump_dialogue()


class GptCommand(Command):
    usage_en = USAGE_EN
    usage_zh_TW = USAGE_ZH_TW

    def __init__(
        self, subcommand: typing.Optional[str] = None, args: typing.Optional[str] = None
    ) -> None:
        super().__init__(subcommand, args)
        self.gpt_sessions: GPTSessions = None

    def load(self, gpt_sessions: GPTSessions):
        self.gpt_sessions = gpt_sessions

    @classmethod
    def setup(cls, args_msg: str) -> GptCommand:
        mrx = re.search(r"(\w+) *(.*)?", args_msg)
        subcommand, args = mrx.groups()
        return cls(subcommand, args)

    def execute(self, **kwargs):
        id = kwargs["id"]
        try:
            func = getattr(self.gpt_sessions, self.subcommand)
            if self.subcommand == "talk":
                return func(id, self.args)
            return func(id)
        except AttributeError:
            return Error(MESSAGE.NOT_ALLOW_METHOD.value)
