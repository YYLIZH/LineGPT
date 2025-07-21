import pytest
from linebot.v3.messaging import (
    FlexMessage,
    LocationMessage,
    TextMessage,
)

from api.commands import googlemap, print_usage

from . import line_handler


@pytest.fixture(name="fake_location")
def fixture_location_message():
    return LocationMessage(
        title="fake location",
        address="fake address",
        latitude=25.033611,
        longitude=121.564444,
    )


def test_print_usage(snapshot):
    help_message = print_usage()[0].text
    assert snapshot == help_message


def test_reply_text_message():
    text_message = TextMessage(text="aaa")
    messages = line_handler.reply_text_message(text_message)
    assert messages is None

    text_message = TextMessage(text="@LineGPT gogo")
    messages = line_handler.reply_text_message(text_message)
    assert messages[0].text == print_usage()[0].text

    text_message = TextMessage(text="@LineGPT help")
    messages = line_handler.reply_text_message(text_message)
    assert messages[0].text == print_usage()[0].text


def test_reply_text_message_eat():
    text_message = TextMessage(text="@LineGPT eat")
    messages = line_handler.reply_text_message(text_message)
    assert isinstance(messages[0], FlexMessage)


def test_reply_text_message_gpt(snapshot):
    text_message = TextMessage(text="@LineGPT gpt")
    messages = line_handler.reply_text_message(text_message)
    assert messages[0].text == snapshot


def test_reply_text_message_settle(snapshot):
    text_message = TextMessage(text="@LineGPT settle")
    messages = line_handler.reply_text_message(text_message)
    assert messages[0].text == snapshot


def test_reply_text_message_weather(snapshot):
    text_message = TextMessage(text="@LineGPT weather")
    messages = line_handler.reply_text_message(text_message)
    assert messages[0].text == snapshot


def test_reply_text_message_toilet():
    text_message = TextMessage(text="@LineGPT toilet")
    messages = line_handler.reply_text_message(text_message)
    assert isinstance(messages[0], FlexMessage)


def test_reply_location_message_no_existing_session(
    fake_location: LocationMessage,
):
    googlemap.GOOGLE_MAP_SESSION.reset()
    assert googlemap.GOOGLE_MAP_SESSION.is_expired() is True
    messages = line_handler.reply_location_message(
        location_message=fake_location
    )
    assert messages is None


def test_reply_location_message_eat(fake_location: LocationMessage):
    googlemap.GOOGLE_MAP_SESSION.set_app("eat")
    messages = line_handler.reply_location_message(
        location_message=fake_location
    )
    print(messages)
    assert messages[0].alt_text == "restaurant cards"


def test_reply_location_message_toilet(
    fake_location: LocationMessage,
):
    googlemap.GOOGLE_MAP_SESSION.set_app("toilet")
    messages = line_handler.reply_location_message(
        location_message=fake_location
    )
    assert messages[0].alt_text == "toilet cards"
