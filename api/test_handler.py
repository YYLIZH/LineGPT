import pytest
from linebot.v3.messaging import LocationMessage, TextMessage

from api.commands import eat, print_usage, toilet

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
    help_message = print_usage()
    assert snapshot == help_message


def test_reply_text_message():
    text_message = TextMessage(text="aaa")
    messages = line_handler.reply_text_message(text_message)
    assert messages is None

    text_message = TextMessage(text="@LineGPT gogo")
    messages = line_handler.reply_text_message(text_message)
    assert messages[0].text == print_usage()

    text_message = TextMessage(text="@LineGPT help")
    messages = line_handler.reply_text_message(text_message)
    assert messages[0].text == print_usage()


def test_reply_text_message_eat(snapshot):
    text_message = TextMessage(text="@LineGPT eat")
    messages = line_handler.reply_text_message(text_message)
    assert messages[0].text == snapshot


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


def test_reply_text_message_toilet(snapshot):
    text_message = TextMessage(text="@LineGPT toilet")
    messages = line_handler.reply_text_message(text_message)
    assert messages[0].text == snapshot


def test_reply_location_message_no_existing_session(
    fake_location: LocationMessage,
):
    assert eat.GOOGLE_MAP_SESSION.is_expired()
    assert toilet.GOOGLE_MAP_SESSION.is_expired()
    messages = line_handler.reply_location_message(
        location_message=fake_location
    )
    assert messages is None


def test_reply_location_message_multiple_existing_session(
    snapshot, fake_location: LocationMessage
):
    eat.GOOGLE_MAP_SESSION.update_time()
    toilet.GOOGLE_MAP_SESSION.update_time()
    messages = line_handler.reply_location_message(
        location_message=fake_location
    )
    assert messages[0].text == snapshot
    eat.GOOGLE_MAP_SESSION.set_expired()
    toilet.GOOGLE_MAP_SESSION.set_expired()


def test_reply_location_message_eat(fake_location: LocationMessage):
    eat.GOOGLE_MAP_SESSION.update_time()
    messages = line_handler.reply_location_message(
        location_message=fake_location
    )
    print(messages)
    assert messages[0].alt_text == "restaurant cards"
    eat.GOOGLE_MAP_SESSION.set_expired()


def test_reply_location_message_toilet(
    fake_location: LocationMessage,
):
    toilet.GOOGLE_MAP_SESSION.update_time()
    messages = line_handler.reply_location_message(
        location_message=fake_location
    )
    assert messages[0].alt_text == "toilet cards"
    toilet.GOOGLE_MAP_SESSION.set_expired()
