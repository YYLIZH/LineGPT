import re

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    Message,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    LocationMessageContent,
    MessageEvent,
    TextMessageContent,
)
from pydantic.v1 import StrictStr

from api.commands import (
    eat,
    googlemap,
    gpt,
    print_usage,
    settle,
    toilet,
    weather,
)
from api.utils.configs import (
    LINE_CHANNEL_ACCESS_TOKEN,
    LINE_CHANNEL_SECRET,
)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
line_handler = WebhookHandler(channel_secret=LINE_CHANNEL_SECRET)


def reply_text_message(
    message: TextMessageContent,
) -> list[TextMessage] | None:
    if not message.text.startswith("@LineGPT"):
        return None

    mrx = re.search(r"^@LineGPT\s+(\w+)\s*.*", message.text)
    if mrx is None:
        return [TextMessage(text=print_usage())]

    message = re.sub(r"^@LineGPT\s+", "", message.text, count=1)
    match mrx.group(1):
        case "eat":
            return eat.handle_message(message)
        case "gpt":
            return gpt.handle_message(message)
        case "settle":
            return settle.handle_message(message)
        case "weather":
            return weather.handle_message(message)
        case "toilet":
            return toilet.handle_message(message)
        case "help":
            return print_usage()
        case _:
            return print_usage()


def reply_location_message(
    location_message: LocationMessageContent,
) -> list[Message] | None:
    if googlemap.GOOGLE_MAP_SESSION.is_expired() is True:
        return None

    match googlemap.GOOGLE_MAP_SESSION.app:
        case "eat":
            return eat.handle_location_message(location_message)
        case "toilet":
            return toilet.handle_location_message(location_message)
        case _:
            return [
                TextMessage(
                    text=f"Unknown app: {googlemap.GOOGLE_MAP_SESSION.app}"
                )
            ]

    return [TextMessage(text="Unexpected error.")]


def send_message(
    reply_token: StrictStr | None, messages: list[Message]
):
    if reply_token is None:
        return

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=messages,
            )
        )


@line_handler.add(MessageEvent, message=TextMessageContent)
def handling_text_message(event: MessageEvent):
    if not event.message:
        return

    messages = reply_text_message(message=event.message)
    if messages is None:
        return
    send_message(reply_token=event.reply_token, messages=messages)


@line_handler.add(MessageEvent, message=LocationMessageContent)
def handling_location_message(event: MessageEvent):
    if not event.message:
        return

    messages = reply_location_message(location_message=event.message)
    if messages is None:
        return
    send_message(reply_token=event.reply_token, messages=messages)
