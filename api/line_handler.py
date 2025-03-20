import re

from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    FlexSendMessage,
    LocationMessage,
    MessageEvent,
    TextMessage,
    TextSendMessage,
)

from api.commands import eat, gpt, print_usage, settle, weather
from api.utils.configs import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(LINE_CHANNEL_SECRET)


def handle_message(message: str) -> str:
    mrx = re.search(r"^@LineGPT\s+(\w+)\s*.*", message)
    if mrx is None:
        return print_usage()

    message = re.sub(r"^@LineGPT\s+", "", message, count=1)
    match mrx.group(1):
        case "eat":
            return eat.handle_message(message)
        case "gpt":
            return gpt.handle_message(message)
        case "settle":
            return settle.handle_message(message)
        case "weather":
            return weather.handle_message(message)
        case "help":
            return print_usage()
        case _:
            return print_usage()


@line_handler.add(MessageEvent, message=TextMessage)
def handling_text_message(event: MessageEvent):
    replyToken = event.reply_token
    if event.message:
        message: str = event.message.text
        if message.startswith("@LineGPT"):
            result = handle_message(message=message)
            if result:
                echoMessages = TextSendMessage(text=result)
                line_bot_api.reply_message(
                    reply_token=replyToken, messages=echoMessages
                )


@line_handler.add(MessageEvent, message=LocationMessage)
def handling_location_message(event: MessageEvent):
    replyToken = event.reply_token
    location_message: LocationMessage = event.message
    if event.message and eat.GoogleMapSession.is_expired() is False:
        result = eat.what_to_eat(
            latitude=location_message.latitude,
            longitude=location_message.longitude,
        )
        flex_message = FlexSendMessage("restaurant cards", result)
        line_bot_api.reply_message(
            reply_token=replyToken, messages=flex_message
        )
