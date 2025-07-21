from linebot.v3.messaging import FlexMessage

from api.commands import toilet


def test_get_toilets(snapshot):
    latitude = 25.033611
    longitude = 121.564444
    toilets = toilet.get_toilets(latitude, longitude)
    assert snapshot == toilets[0]


def test_print_help(snapshot):
    help_message = toilet.print_help()
    assert snapshot == help_message


def test_handle_message_toilet():
    msg = toilet.handle_message("toilet")
    assert isinstance(msg[0], FlexMessage)

    msg = toilet.handle_message("toilet help")
    assert msg[0].text == toilet.print_help()

    assert (
        toilet.handle_message("toilet help aaa")[0].text
        == toilet.handle_message("toilet aaa help")[0].text
    )
