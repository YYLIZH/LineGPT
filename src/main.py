from fastapi import FastAPI, Request, HTTPException

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from .linegpt import LineGPT

LINE_CHANNEL_SECRET="6dbe97eaaffd3465ef913914651cd8d6"
LINE_CHANNEL_ACCESS_TOKEN="z3zyjJHraYiDTQ0fCKYL8iLQawbQgy8WxYMh8SZNIjnnfIL5vRGowii5NAL/t+p8PrSMRaWEnMC10gZs0LnPcwyRJgVfLuN/ppL5aedth5NnTeFwm5SC9nUvxYFonVd7+Mpi5eWrJRKdwKr2qY5a/gdB04t89/1O/w1cDnyilFU="

app = FastAPI()
lineGPT=LineGPT()


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
            gpt_message=lineGPT.select_command(message)
            echoMessages = TextSendMessage(text=gpt_message)
            line_bot_api.reply_message(reply_token=replyToken, messages=echoMessages)
