HELP_TEXT = """Hi! I am LineGPT. It's my pleasure to help you. Here is the usage:
@LineGPT <Command>

* Show help text
@LineGPT help

* Start a dialogue session.
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

SELECT_COMMAND_ERROR = "Error: Unknown command. Please type again or type '@LineGPT help' for more information."

START_GREETING = "Start the dialogue session. You can ask question now."
START_FOUND_SESSION = "Found existing session. You can see existing session's dialog, keep asking question, or restart a new session."

ASK_NO_SESSION_WARNING = (
    "Warning: Session does not exist. Please start the session first."
)
ASK_EXPIRED_WARNING = (
    "Warning: Current dialogue session is expired. Please restart the dialogue session."
)
ASK_QUESTION_RUNTIME_ERROR = "Error: RuntimeError. Please ask again later."

CLOSE_MESSAGE = "Close current dialogue session."

RESTART_MESSAGE = "Restart the dialogue session"

LOG_MESSAGE = "Below are the past dialogues:"
