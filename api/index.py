from fastapi import FastAPI, HTTPException, Request
from linebot.exceptions import InvalidSignatureError

from api.linebot import line_handler

app = FastAPI()


@app.get("/")
async def home(request: Request):
    return {"LineGPT": "Test"}


@app.get("/webhook")
async def checkWebhook(request: Request):
    return {"webhook": "OK"}


@app.post("/webhook")
async def LineAgent(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        line_handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(
            status_code=400, detail="Missing Parameters"
        )
    return "OK"
