import datetime
import os
import re

import openai

from api.messages import static_messages

openai.api_key = os.getenv("OPENAI_API_KEY")


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
        if time_delta.seconds >= 10 * 60:
            return True
        return False


class LineGPT:
    def __init__(self) -> None:
        self.dialogue_session = None
        self.model = os.getenv("OPENAI_MODEL", default="text-davinci-003")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default=1))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKEN", default=16))
        self.frequency_penalty = float(
            os.getenv("OPENAI_FREQUENCY_PENALTY", default=0.0)
        )
        self.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", default=0.0))

    def ask_gpt(self):
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
        self.dialogue_session.add_ai_text(extracted_text)
        return extracted_text

    def select_command(self, command_str: str):
        if re.match("^@LineGPT *$", command_str):
            return self.command_help()
        pattern = re.compile(r"^@LineGPT *(\w+) *(.*)")
        mrx = pattern.search(command_str)

        if not mrx:
            return static_messages["SELECT_COMMAND_ERROR"]
        command = mrx.group(1)
        if command == "help":
            return self.command_help()
        if command == "start":
            return self.command_start()
        if command == "ask":
            return self.command_ask(mrx.group(2))
        if command == "close":
            return self.command_close()
        if command == "restart":
            return self.command_restart()
        if command == "log":
            return self.command_log()
        return static_messages["SELECT_COMMAND_ERROR"]

    def command_help(self):
        return static_messages["HELP_TEXT"]

    def command_start(self):
        if self.dialogue_session is None:
            self.dialogue_session = DialogueSession()
            return static_messages["START_GREETING"]
        return static_messages["START_FOUND_SESSION"]

    def command_ask(self, text):
        if self.dialogue_session is None:
            return static_messages["ASK_NO_SESSION_WARNING"]
        if self.dialogue_session.is_expired():
            return static_messages["ASK_EXPIRED_WARNING"]

        self.dialogue_session.add_human_text(text)
        try:
            response = self.ask_gpt()
        except Exception:
            self.dialogue_session.dialogue.pop()
            return static_messages["ASK_QUESTION_RUNTIME_ERROR"]
        return response

    def command_close(self):
        self.dialogue_session = None
        return static_messages["CLOSE_MESSAGE"]

    def command_restart(self):
        self.dialogue_session = DialogueSession()
        return static_messages["RESTART_MESSAGE"]

    def command_log(self):
        return (
            static_messages["LOG_MESSAGE"]
            + "\n"
            + self.dialogue_session.dump_dialogue()
        )
