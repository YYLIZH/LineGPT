from datetime import datetime, timedelta
from typing import Literal


class GoogleMapSession:
    timeout = 180

    def __init__(self):
        self.last_update_time = datetime.now() - timedelta(days=1)
        self.app = None

    def is_expired(self) -> bool:
        expired_time = self.last_update_time + timedelta(
            seconds=self.timeout
        )
        if datetime.now() > expired_time:
            return True
        return False

    def reset(self):
        self.app = None
        self.last_update_time = datetime.now() - timedelta(days=1)

    def set_app(self, app: Literal["eat", "toilet"]):
        self.last_update_time = datetime.now()
        self.app = app


GOOGLE_MAP_SESSION = GoogleMapSession()
