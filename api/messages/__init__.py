import importlib
import os
# from api.messages import zh as module
language = os.getenv("LANGUAGE", default="zh")


module = importlib.import_module(f"api.messages.{language}")

static_messages = {
    "HELP_TEXT": module.HELP_TEXT,
    "SELECT_COMMAND_ERROR": module.SELECT_COMMAND_ERROR,
    "START_GREETING": module.START_GREETING,
    "START_FOUND_SESSION": module.START_FOUND_SESSION,
    "ASK_NO_SESSION_WARNING": module.ASK_NO_SESSION_WARNING,
    "ASK_EXPIRED_WARNING": module.ASK_EXPIRED_WARNING,
    "ASK_QUESTION_RUNTIME_ERROR": module.ASK_QUESTION_RUNTIME_ERROR,
    "CLOSE_MESSAGE": module.CLOSE_MESSAGE,
    "RESTART_MESSAGE": module.RESTART_MESSAGE,
    "LOG_MESSAGE": module.LOG_MESSAGE,
}
