from unittest import mock

from api.commands.gpt import GPT, GptCommand, GPTSessions, MessageEN, MessageZH


class TestGPTSession:
    @classmethod
    def setup_class(cls):
        cls.gpt_sessions = GPTSessions()
        cls.gpt_sessions.sessions["test123"] = GPT()
        cls.gpt_sessions.sessions["test123"].dialogue_session.add_human_text("hello")
        cls.gpt_sessions.sessions["test123"].dialogue_session.add_ai_text("hi")

    def test_start(self):
        res = self.gpt_sessions.start("test456")
        assert isinstance(self.gpt_sessions.sessions.get("test456"), GPT)

    @mock.patch("openai.Completion.create")
    def test_talk(self, mock_openai):
        mock_openai.return_value = {"choices": [{"text": "ai result\n"}]}
        res = self.gpt_sessions.talk("test456", "human ask")
        mock_openai.assert_called_once()
        assert res == "ai result"

    def test_log(self):
        res = self.gpt_sessions.log("test123")
        assert (
            res == MessageEN.LOG.value + "\n" + "Human: hello\n" + "AI: hi"
            or res == MessageZH.LOG.value + "\n" + "Human: hello\n" + "AI: hi"
        )

    def test_close(self):
        res = self.gpt_sessions.close("test456")
        assert "test456" not in list(self.gpt_sessions.sessions.keys())


def test_help():
    command = GptCommand()
    result = command.print_usage()
    assert result == GptCommand.usage_en or result == GptCommand.usage_zh
