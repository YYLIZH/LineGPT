import textwrap
from datetime import datetime, timedelta

from api.commands import gpt


class TestDialogueSession:
    @classmethod
    def setup_class(cls):
        cls.session = gpt.DialogueSession()

    def test_is_expired(self):
        assert self.session.is_expired is False

        self.session.last_update_time = datetime.now() - timedelta(
            days=1
        )
        assert self.session.is_expired is True

    def test_talk(self):
        response = self.session.talk(
            "Who won the world series in 2020?"
        )
        assert response != ""


class TestGPT:
    @classmethod
    def setup_class(cls):
        cls.gpt = gpt.GPT()

    def test_start(self):
        res = self.gpt.start()
        assert res == gpt.MESSAGE.GREETING.value

        res = self.gpt.start()
        assert res == gpt.MESSAGE.FOUND_SESSION.value

    def test_talk(self):
        res = self.gpt.talk("Who won the world series in 2020?")
        assert res != ""

    def test_log(self, snapshot):
        self.gpt.restart()
        self.gpt.log()
        log_tw = textwrap.dedent(
            """
            system: You are a helpful assistant. Please respond in 繁體中文.
            user: hello
            assistant: hi
            """
        )
        log_en = textwrap.dedent(
            """
            system: You are a helpful assistant. Please respond in en.
            user: hello
            assistant: hi
            """
        )
        assert snapshot == gpt.MESSAGE.LOG.value + "\n" + log_tw

    def test_close(self):
        res = self.gpt.close()
        assert res == gpt.MESSAGE.CLOSE.value
        assert self.gpt.dialogue_session is None

    def test_restart(self):
        self.gpt.restart()

        assert self.gpt.dialogue_session.dialogue == [
            {
                "role": "system",
                "content": "You are a helpful assistant. Please respond in 繁體中文.",
            }
        ] or self.gpt.dialogue_session.dialogue == [
            {
                "role": "system",
                "content": "You are a helpful assistant. Please respond in 'en'.",
            }
        ]


def test_help(snapshot):
    assert snapshot == gpt.print_help()
