import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from linebot.v3.exceptions import InvalidSignatureError

from api.commands.googlemap import GOOGLE_MAP_SESSION
from api.line_handler import line_handler

app = FastAPI()


@app.get("/")
async def home(request: Request):
    session = "activated"
    if GOOGLE_MAP_SESSION.is_expired():
        session = "unactivated"
    else:
        session = GOOGLE_MAP_SESSION.app

    return {
        "LineGPT": "Test",
        "session": session,
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


app.mount(
    "/static",
    StaticFiles(
        directory=os.path.join(os.path.dirname(__file__), "static")
    ),
    name="static",
)
