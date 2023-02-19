import datetime
import os
import re

import openai


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
