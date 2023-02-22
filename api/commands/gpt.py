import datetime
import re
from enum import Enum
from typing import Dict

import openai

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
    FOUND_SESSION = "Found existing session. You can see existing session's dialog, keep asking question, or restart a new session."
    NO_SESSION = "Session does not exist. Please start the session first."
    SESSION_EXPIRED = (
        "Current dialogue session is expired. Please restart the dialogue session."
    )
    RUNTIME_ERROR = "RuntimeError. Please ask again later."
    UNEXPECTED_ERROR = "Unexpected error happened. Restart the session."
    CLOSE = "Close current dialogue session."
    RESTART = "Restart the dialogue session"
    LOG = "Below are the past dialogues:"


class MessageZH(Enum):
    GREETING = "對話階段已開始"
    FOUND_SESSION = "存在舊有的對話階段，您可以查看紀錄、繼續對話、或是重啟對話階段。"
    NO_SESSION = '尚未開啟對話階段，請先使用"@LineGPT start"開啟對話。'
    SESSION_EXPIRED = '當前對話階段已過期。請先使用"@LineGPT restart"重新開啟對話階段。'
    RUNTIME_ERROR = "RuntimeError. 請稍後再試一次"
    UNEXPECTED_ERROR = "發生未知的錯誤，重啟對話。"
    CLOSE = "關閉對話階段。"
    RESTART = "重新啟動對話階段"
    LOG = "以下是對話紀錄："


openai.api_key = OPENAI_API_KEY
MESSAGE = MessageEN if LANGUAGE == "en" else MessageZH


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
        if time_delta.seconds >= SESSION_EXPIRED:
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

    def talk(self, group_id: str, text: str) -> str:
        gpt = self.sessions.get(group_id)
        try:
            return gpt.talk(text)
        except Exception:
            self.sessions[group_id] = GPT()
            return Error(MESSAGE.UNEXPECTED_ERROR.value)

    def log(self, group_id: str) -> str:
        gpt = self.sessions.get(group_id)
        return MESSAGE.LOG + "\n" + gpt.dialogue_session.dump_dialogue()
