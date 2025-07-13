import re

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    FlexContainer,
    FlexMessage,
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
) -> list[Message] | None:
    if not message.text.startswith("@LineGPT"):
        return None

    mrx = re.search(r"^@LineGPT\s+(\w+)\s*.*", message.text)
    if mrx is None:
        return [TextMessage(text=print_usage())]

    message = re.sub(r"^@LineGPT\s+", "", message.text, count=1)
    match mrx.group(1):
        case "eat":
            return [TextMessage(text=eat.handle_message(message))]
        case "gpt":
            return [TextMessage(text=gpt.handle_message(message))]
        case "settle":
            return [TextMessage(text=settle.handle_message(message))]
        case "weather":
            return [TextMessage(text=weather.handle_message(message))]
        case "toilet":
            return [TextMessage(text=toilet.handle_message(message))]
        case "help":
            return [TextMessage(text=print_usage())]
        case _:
            return [TextMessage(text=print_usage())]


def reply_location_message(
    location_message: LocationMessageContent,
) -> list[Message] | None:
    if (
        toilet.GOOGLE_MAP_SESSION.is_expired() is True
        and eat.GOOGLE_MAP_SESSION.is_expired() is True
    ):
        return None

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

    elif eat.GOOGLE_MAP_SESSION.is_expired() is False:
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

    elif toilet.GOOGLE_MAP_SESSION.is_expired() is False:
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

    return messages


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
