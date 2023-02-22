import re
from importlib import import_module

from fastapi import FastAPI, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from api.commands.base import Command
from api.commands.gpt import GPTSessions
from api.utils.configs import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET

app = FastAPI()
GPT_Sessions = GPTSessions()
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(LINE_CHANNEL_SECRET)


def parse_command(message: str) -> Command:
    mrx = re.search(r"^@LineGPT +(\w+)( +\w+)? +(.*)", message)
    command_str, subcommand_str, args = mrx.groups()
    module = import_module(f"api.commands.{command_str}")
    command_cls = getattr(module, f"{command.title()}Command")
    command = command_cls(subcommand_str, args)
    if command_str == "gpt":
        command.load(GPT_Sessions)
    return command


@app.get("/")
async def home(request: Request):
    return {"LineGPT": "Test"}


@app.get("/webhook")
async def checkWebhook(request: Request):
    return {"webhook": "OK"}


@app.post("/webhook")
async def LineGPTBot(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        line_handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameters")
    return "OK"


@line_handler.add(MessageEvent, message=TextMessage)
def handling_message(event):
    replyToken = event.reply_token
    if event.message:
        message: str = event.message.text
        if message.startswith("@LineGPT"):
            try:
                id = getattr(event.source, "group_id")
            except AttributeError:
                id = getattr(event.source, "user_id")
            command: Command = parse_command(message, GPT_Sessions)
            result = command.execute(**{"id": id})
            if result:
                echoMessages = TextSendMessage(text=result)
                line_bot_api.reply_message(
                    reply_token=replyToken, messages=echoMessages
                )
