import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

BASE_DIR = os.path.dirname(__file__)

load_dotenv()

from api.linegpt import LineGPT

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if (
    LINE_CHANNEL_SECRET == "hakuna-matata"
    or LINE_CHANNEL_ACCESS_TOKEN == "hakuna-matata"
):
    raise ValueError("Please set the .env value correctly.")

app = FastAPI()
lineGPT = LineGPT()
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(LINE_CHANNEL_SECRET)


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
        message = event.message.text
        if message.startswith("@LineGPT"):
            gpt_message = lineGPT.select_command(message)
            echoMessages = TextSendMessage(text=gpt_message)
            line_bot_api.reply_message(reply_token=replyToken, messages=echoMessages)