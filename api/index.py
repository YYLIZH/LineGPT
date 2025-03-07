import re
from importlib import import_module
from typing import Union

from fastapi import FastAPI, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    FlexSendMessage,
    LocationMessage,
    MessageEvent,
    TextMessage,
    TextSendMessage,
)

from api.commands import commands_info, print_usage
from api.commands.base import Command
from api.commands.eat import EatCommand, GoogleMapSession, what_to_eat
from api.commands.gpt import GptCommand, GPTSessions
from api.utils.configs import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
)
from api.utils.info import Error

app = FastAPI()
GPT_Sessions = GPTSessions()
GoogleMap_Session = GoogleMapSession()
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(LINE_CHANNEL_SECRET)


def parse_message(message: str) -> Union[str, Command]:
    if re.match(r"^@LineGPT( help.*)?$", message):
        return print_usage()
    mrx = re.search(r"^@LineGPT +(\w+) *([\s\S]*)", message)
    if not mrx:
        return str(Error("Wrong format")) + "\n" + print_usage()
    command_str, other = mrx.groups()
    command_info = commands_info.get(command_str)
    if not command_info:
        return str(Error("No such command")) + "\n" + print_usage()
    module = import_module(command_info.module_path)
    command_cls: Command = getattr(module, command_info.class_name)
    command = command_cls.setup(other)
    if "help" in message:
        return command_cls.print_usage()
    if isinstance(command, GptCommand):
        command.load(GPT_Sessions)
    elif isinstance(command, EatCommand):
        GoogleMap_Session.update_time()
        command.load(GoogleMap_Session)
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
def handling_text_message(event):
    replyToken = event.reply_token
    if event.message:
        message: str = event.message.text
        if message.startswith("@LineGPT"):
            try:
                id = getattr(event.source, "group_id")
            except AttributeError:
                id = getattr(event.source, "user_id")
            parse_result = parse_message(message)
            if isinstance(parse_result, Command):
                command: Command = parse_result
                result = command.execute(**{"id": id})
            else:
                result = parse_result

            if result:
                echoMessages = TextSendMessage(text=str(result))
                line_bot_api.reply_message(
                    reply_token=replyToken, messages=echoMessages
                )


@line_handler.add(MessageEvent, message=LocationMessage)
def handling_location_message(event):
    replyToken = event.reply_token
    if event.message and GoogleMap_Session.is_expired() is False:
        latitude = event.message.latitude
        longitude = event.message.longitude
        result = what_to_eat(latitude, longitude)
        flex_message = FlexSendMessage("cards", result)
        line_bot_api.reply_message(reply_token=replyToken, messages=flex_message)
