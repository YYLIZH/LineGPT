from fastapi import FastAPI, HTTPException, Request
from linebot.v3.exceptions import InvalidSignatureError

from api.commands import eat, toilet
from api.line_handler import line_handler

app = FastAPI()


@app.get("/")
async def home(request: Request):
    eat_session = "activated"
    if eat.GOOGLE_MAP_SESSION.is_expired():
        eat_session = "unactivated"

    toilet_session = "activated"
    if toilet.GOOGLE_MAP_SESSION.is_expired():
        toilet_session = "unactivated"

    return {
        "LineGPT": "Test",
        "eat": eat_session,
        "toilet": toilet_session,
    }


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
