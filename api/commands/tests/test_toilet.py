from datetime import datetime

from api.commands import toilet


def test_get_toilets(snapshot):
    latitude = "24.785057"
    longitude = "121.017385"
    toilets = toilet.get_toilets(latitude, longitude)
    assert snapshot == toilets[0]


class TestGoogleMapSession:
    def test_init(self):
        session = toilet.GoogleMapSession()
        assert (datetime.now() - session.last_update_time).days >= 1

    def test_update_time(self):
        session = toilet.GoogleMapSession()
        session.update_time()
        assert (
            datetime.now() - session.last_update_time
        ).seconds < 10

    def test_is_expired(self):
        session = toilet.GoogleMapSession()
        assert session.is_expired() is True

        session.update_time()
        assert session.is_expired() is False

    def test_set_expired(self):
        session = toilet.GoogleMapSession()
        session.update_time()
        session.set_expired()
        assert session.is_expired() is True


def test_print_help(snapshot):
    help_message = toilet.print_help()
    assert snapshot == help_message


def test_handle_message_toilet():
    msg = toilet.handle_message("toilet start")
    assert msg == toilet.MESSAGE.START_REPLY.value

    msg = toilet.handle_message("toilet stop")
    assert msg == toilet.MESSAGE.STOP_REPLY.value

    msg = toilet.handle_message("toilet help")
    assert msg == toilet.print_help()

    assert toilet.handle_message(
        "toilet help aaa"
    ) == toilet.handle_message("toilet aaa help")
