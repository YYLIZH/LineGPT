from unittest import mock

from api.commands.gpt import GPT, GptCommand, GPTSessions, MessageEN, MessageZHTW


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

    @mock.patch("openai.ChatCompletion.create")
    def test_talk(self, mock_openai):
        mock_openai.return_value = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "index": 0,
                    "message": {
                        "content": "The Los Angeles Dodgers won the World Series in 2020.",
                        "role": "assistant",
                    },
                }
            ],
            "created": 1678814998,
            "id": "xxx",
            "model": "gpt-3.5-turbo-0301",
            "object": "chat.completion",
            "usage": {"completion_tokens": 19, "prompt_tokens": 56, "total_tokens": 75},
        }
        res = self.gpt_sessions.talk("test456", "Who won the world series in 2020?")
        mock_openai.assert_called_once()
        assert res == "The Los Angeles Dodgers won the World Series in 2020."

    def test_log(self):
        res = self.gpt_sessions.log("test123")
        log_tw = """    system: You are a helpful assistant. Please respond in 'zh_TW'.
      user: hello
 assistant: hi
"""
        log_en = """    system: You are a helpful assistant. Please respond in 'en'.
      user: hello
 assistant: hi
"""
        assert (
            res == MessageZHTW.LOG.value + "\n" + log_tw
            or res == MessageEN.LOG.value + "\n" + log_en
        )

    def test_close(self):
        res = self.gpt_sessions.close("test456")
        assert "test456" not in list(self.gpt_sessions.sessions.keys())

    def test_restart(self):
        self.gpt_sessions.restart("test123")

        assert self.gpt_sessions.sessions["test123"].dialogue_session.dialogue == [
            {
                "role": "system",
                "content": "You are a helpful assistant. Please respond in 'zh_TW'.",
            }
        ] or self.gpt_sessions.sessions["test123"].dialogue_session.dialogue == [
            {
                "role": "system",
                "content": "You are a helpful assistant. Please respond in 'en'.",
            }
        ]


def test_help():
    command = GptCommand()
    result = command.print_usage()
    assert result == GptCommand.usage_en or result == GptCommand.usage_zh_TW
