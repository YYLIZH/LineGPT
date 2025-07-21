from datetime import datetime

from api.commands.googlemap import GoogleMapSession


class TestGoogleMapSession:
    def test_init(self):
        session = GoogleMapSession()
        assert (datetime.now() - session.last_update_time).days >= 1

    def test_is_expired(self):
        session = GoogleMapSession()
        assert session.is_expired() is True

    def test_set_app(self):
        session = GoogleMapSession()
        assert session.is_expired() is True

        session.set_app("eat")
        assert session.is_expired() is False
