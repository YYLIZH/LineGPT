from api.commands import gpt


class TestGPTSession:
    @classmethod
    def setup_class(cls):
        cls.gpt_sessions = gpt.GPTSessions()
        cls.gpt_sessions.sessions["test123"] = gpt.GPT()
        cls.gpt_sessions.sessions[
            "test123"
        ].dialogue_session.add_human_text("hello")
        cls.gpt_sessions.sessions[
            "test123"
        ].dialogue_session.add_ai_text("hi")

    def test_start(self):
        res = self.gpt_sessions.start("test456")
        assert isinstance(
            self.gpt_sessions.sessions.get("test456"), gpt.GPT
        )

    def test_talk(self):
        res = self.gpt_sessions.talk(
            "test456", "Who won the world series in 2020?"
        )
        assert res != ""

    def test_log(self):
        res = self.gpt_sessions.log("test123")
        log_tw = """    system: You are a helpful assistant. Please respond in 繁體中文.
      user: hello
 assistant: hi
"""
        log_en = """    system: You are a helpful assistant. Please respond in en.
      user: hello
 assistant: hi
"""
        assert (
            res == gpt.MessageZHTW.LOG.value + "\n" + log_tw
            or res == gpt.MessageEN.LOG.value + "\n" + log_en
        )

    def test_close(self):
        res = self.gpt_sessions.close("test456")
        assert "test456" not in list(
            self.gpt_sessions.sessions.keys()
        )

    def test_restart(self):
        self.gpt_sessions.restart("test123")

        assert self.gpt_sessions.sessions[
            "test123"
        ].dialogue_session.dialogue == [
            {
                "role": "system",
                "content": "You are a helpful assistant. Please respond in 繁體中文.",
            }
        ] or self.gpt_sessions.sessions[
            "test123"
        ].dialogue_session.dialogue == [
            {
                "role": "system",
                "content": "You are a helpful assistant. Please respond in 'en'.",
            }
        ]


def test_help():
    command = gpt.GptCommand()
    result = command.print_usage()
    assert (
        result == gpt.GptCommand.usage_en
        or result == gpt.GptCommand.usage_zh_TW
    )
