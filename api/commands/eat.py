from __future__ import annotations
from api.commands.base import Command
from api.utils.configs import GOOGLE_API_KEY, LANGUAGE
from datetime import datetime, timedelta
import textwrap
import requests
from enum import Enum


class MessageEN(str, Enum):
    REPLY = "Please share your location to me"
    NO_RESULT = "No result in nearby location."


class MessageZHTW(str, Enum):
    REPLY = "請分享你的位置資訊給我"
    NO_RESULT = "找不到結果"


MESSAGE = MessageEN if LANGUAGE == "en" else MessageZHTW


def get_restaurants(latitude: str, longitude: str) -> list[dict]:
    radius = 5000
    place_type = "restaurant"
    location = f"{latitude},{longitude}"

    query_opts = [
        f"location={location}",
        f"radius={radius}",
        f"type={place_type}",
        f"key={GOOGLE_API_KEY}",
        "opennow=true",
    ]
    if LANGUAGE == "zh_TW":
        query_opts.append("language=zh-TW")

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?" + "&".join(
        query_opts
    )

    try:
        response = requests.get(url)
        data = response.json()
        return sorted(data["results"], key=lambda x: x["rating"], reverse=True)
    except Exception:
        return []


def create_map_link(place_id: str) -> str:
    map_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    return map_link


def what_to_eat(latitude: str, longitude: str) -> str:
    restaurants = get_restaurants(latitude, longitude)
    if len(restaurants) == 0:
        return MESSAGE.NO_RESULT.value

    # Format the text
    result = []
    for restaurant in restaurants:
        stack = []
        url = create_map_link(restaurant["place_id"])
        stack.append(restaurant["name"])
        stack.append(f"\t\tRating: {restaurant['rating']}")
        stack.append(f"\t\t# of Ratings: {restaurant['user_ratings_total']}")
        stack.append(f"\t\tURL: {url}")
        result.append("\n".join(stack))

    return "\n".join(result)


class GoogleMapSession:
    timeout = 5

    def __init__(self):
        self.last_update_time = datetime.now() - timedelta(days=1)

    def update_time(self):
        self.last_update_time = datetime.now()

    def is_expired(self) -> bool:
        expired_time = self.last_update_time + timedelta(minutes=self.timeout)
        if datetime.now() > expired_time:
            return True
        return False


class EatCommand(Command):
    usage_en = textwrap.dedent(
        """
        * Find opening restaurant nearby.

        Example:
        @LineGPT eat
        """
    )

    usage_zh_TW = textwrap.dedent(
        """
        * 尋找附近的餐廳

        Example: 
        @LineGPT eat
        """
    )

    def __init__(self, subcommand=None, args=None):
        super().__init__(subcommand, args)
        self.google_map_session = None

    @classmethod
    def setup(cls, args_msg: str) -> EatCommand:
        return cls(None, args_msg)

    def load(self, google_map_session: GoogleMapSession):
        self.google_map_session = google_map_session

    def execute(self, **kwargs):
        return MESSAGE.REPLY.value
