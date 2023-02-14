import os
import openai
import re
import datetime

openai.api_key = "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"

# https://github.com/JokerWuXin/ChatGpt-LineBot

HELP_TEXT = """This is the usage of LineGPT. Tag the LineGPT to awake it and use its command.
@LineGPT <Command>

* Show help text
@LineGPT help

* Start a dialogue session
@LineGPT start

* Show dialogue
@LineGPT log

* Ask a question
@LineGPT ask <your question> 
Example:
@LineGPT ask What is graphene?

* Close an existing dialogue session
@LineGPT close

* Restart a dialogue session
@LineGPT restart
"""


class DialogueSession:
    limited_sentences = 20

    def __init__(self) -> None:
        self.dialogue = []
        self.last_update_time = datetime.datetime.now()

    def add_ai_text(self, text: str) -> None:
        if not text.startswith("AI: "):
            text = "AI: " + text
        self.dialogue.append(f"{text}")

        self.last_update_time = datetime.datetime.now()

    def add_human_text(self, text: str) -> None:
        self.dialogue.append(f"Human: {text}")

        self.last_update_time = datetime.datetime.now()

    def create_prompt(self) -> str:
        return "\n".join(self.dialogue)

    def is_full(self) -> bool:
        return len(self.dialogue) >= self.limited_sentences - 1

    def is_due(self) -> bool:
        time_delta: datetime.timedelta = datetime.datetime.now() - self.last_update_time
        if time_delta.seconds >= 10 * 60:
            return True
        return False


class LineGPT:
    def __init__(self) -> None:
        self.dialogue_session = None

    def get_response(self):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=self.dialogue_session.create_prompt(),
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
        )
        text = response["choices"][0]["text"].strip()
        self.dialogue_session.add_ai_text(text)
        return text

    def select_command(self, command_str: str):
        ERROR_OUTPUT = "Error: Unknown command. Please type again or type '@LineGPT help' for more information."
        pattern = re.compile(r"^@LineGPT *(\w+) *(.*)")

        mrx = pattern.search(command_str)
        if not mrx:
            return ERROR_OUTPUT
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
        return ERROR_OUTPUT

    def command_help(self):
        return HELP_TEXT

    def command_start(self):
        if self.dialogue_session is None:
            self.dialogue_session = DialogueSession()
            return "Start the dialogue session. You can ask question now."
        return "Found existing session. You can see existing dialogue, keep asking question, or restart a new session."

    def command_ask(self, text):
        if self.dialogue_session is None:
            return "Warning: Session does not exist. Please start the session first."
        if self.dialogue_session.is_full():
            return "Warning: Reach the sentence limit of dialogue. Please restart the dialogue session."

        self.dialogue_session.add_human_text(text)
        try:
            response = self.get_response()
        except Exception:
            self.dialogue_session.dialogue.pop()
            return "Error: RuntimeError. Please ask again later."
        return response

    def command_close(self):
        self.dialogue_session = None
        return "Close current dialogue session."

    def command_restart(self):
        self.dialogue_session = DialogueSession()
        return "Restart the dialogue session"

    def command_log(self):
        return self.dialogue_session.create_prompt()
