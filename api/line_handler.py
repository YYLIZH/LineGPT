import re

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    FlexContainer,
    FlexMessage,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    LocationMessageContent,
    MessageEvent,
    TextMessageContent,
)

from api.commands import (
    eat,
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
        case "toilet":
            return toilet.handle_message(message)
        case "help":
            return print_usage()
        case _:
            return print_usage()


@line_handler.add(MessageEvent, message=TextMessageContent)
def handling_text_message(event: MessageEvent):
    if not event.message:
        return

    message: str = event.message.text
    if not message.startswith("@LineGPT"):
        return

    result = handle_message(message=message)
    if result:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=result)],
                )
            )


@line_handler.add(MessageEvent, message=LocationMessageContent)
def handling_location_message(event: MessageEvent):
    replyToken = event.reply_token
    location_message: LocationMessageContent = event.message
    if event.message:
        messages = []
        if (
            toilet.GOOGLE_MAP_SESSION.is_expired() is False
            and eat.GOOGLE_MAP_SESSION.is_expired() is False
        ):
            messages = [
                TextMessage(
                    text="The sessions of both eat and toilet are existing. "
                    "Please stop one of them."
                )
            ]

        if (
            toilet.GOOGLE_MAP_SESSION.is_expired() is True
            and eat.GOOGLE_MAP_SESSION.is_expired() is True
        ):
            messages = [
                TextMessage(
                    text="No session is running. "
                    "Please type '@LineGPT eat start' or '@LineGPT toilet start' to start a location Session."
                )
            ]

        if eat.GOOGLE_MAP_SESSION.is_expired() is False:
            result = eat.what_to_eat(
                latitude=location_message.latitude,
                longitude=location_message.longitude,
            )
            messages = [
                FlexMessage(
                    altText="restaurant cards",
                    contents=FlexContainer.from_dict(result),
                )
            ]

        if toilet.GOOGLE_MAP_SESSION.is_expired() is False:
            result = toilet.where_to_pee(
                latitude=location_message.latitude,
                longitude=location_message.longitude,
            )
            messages = [
                FlexMessage(
                    altText="toilet cards",
                    contents=FlexContainer.from_dict(result),
                )
            ]

        else:
            # This should not happed
            messages = [TextMessage(text="Unexpected error.")]

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token, messages=messages
                )
            )
