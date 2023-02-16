import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

from .linegpt import LineGPT

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if (
    LINE_CHANNEL_SECRET == "hakuna-matata"
    or LINE_CHANNEL_ACCESS_TOKEN == "hakuna-matata"
):
    raise ValueError("Please set the .env value correctly.")

app = FastAPI()
lineGPT = LineGPT(language=os.getenv("LANGUAGE", default="en"))
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.post("/")
async def LineGPTBot(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Missing Parameters")
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handling_message(event):
    replyToken = event.reply_token
    if event.message:
        message = event.message.text
        if message.startswith("@LineGPT"):
            gpt_message = lineGPT.select_command(message)
            echoMessages = TextSendMessage(text=gpt_message)
            line_bot_api.reply_message(reply_token=replyToken, messages=echoMessages)
