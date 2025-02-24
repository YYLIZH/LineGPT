from __future__ import annotations

import math
import textwrap
from datetime import datetime, timedelta
from enum import Enum

import requests

from api.commands.base import Command
from api.utils.configs import GOOGLE_API_KEY, LANGUAGE


class MessageEN(str, Enum):
    REPLY = "Please share your location to me"
    NO_RESULT = "No result in nearby location."


class MessageZHTW(str, Enum):
    REPLY = "請分享你的位置資訊給我"
    NO_RESULT = "找不到結果"


MESSAGE = MessageEN if LANGUAGE == "en" else MessageZHTW


def get_food(latitude: str, longitude: str) -> list[dict]:
    radius = 3000
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
        return sorted(data["results"], key=lambda x: x["rating"], reverse=True)[:10]
    except Exception:
        return []


def create_map_link(latitude: str, longitude: str, place_id: str) -> str:
    map_link = f"https://www.google.com/maps/search/?api=1&query={latitude}%2C{longitude}&query_place_id={place_id}"
    return map_link

def calculate_distance(lat1:float, lon1:float, lat2:float, lon2:float)->str:
    """Use Haversine Formula"""
    # 地球半徑（公里）
    R = 6371.0
    
    # 將經緯度轉換為弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # 經度和緯度的差值
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # 哈弗辛公式
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # 距離（公里）
    distance = R * c

    if distance>1:
        return f"{round(distance,2)} km"

    return f"{round(distance*1000,2)} m"

def get_place_detail(user_lat:str,user_lng:str,place_info: dict) -> dict[str, str]:
    name = str(place_info.get("name", ""))
    rating = place_info.get("rating", 0.0)
    user_ratings_total = place_info.get("user_ratings_total", 0)
    address = str(place_info.get("vicinity", "N/A"))

    latitude = place_info["geometry"]["location"]["lat"]
    longitude = place_info["geometry"]["location"]["lng"]

    return {
        "name": name,
        "address": address,
        "distance":calculate_distance(float(user_lat),float(user_lng),latitude,longitude),
        "rating": rating,
        "user_ratings_total": user_ratings_total,
        "map_url": create_map_link(latitude, longitude, place_info["place_id"]),
    }


def generate_card(
    name: str, address:str,distance:float,rating: float, user_ratings_total: int, map_url: str
) -> dict:
    card = {
        "type": "bubble",
        "size": "micro",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": str(name),
                    "weight": "bold",
                    "size": "sm",
                    "wrap": True,
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [],
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{user_ratings_total} votes",
                            "size": "sm",
                        }
                    ],
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": str(address),
                                    "wrap": True,
                                    "color": "#8c8c8c",
                                    "size": "xs",
                                    "flex": 5,
                                }
                            ],
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": str(distance),
                                    "wrap": True,
                                    "color": "#8c8c8c",
                                    "size": "xs",
                                    "flex": 5,
                                }
                            ],
                        }
                    ],
                },
            ],
            "spacing": "sm",
            "paddingAll": "13px",
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "Go",
                        "uri": map_url,
                    },
                    "style": "primary",
                }
            ],
        },
    }

    # calculate rating box content
    rating_box_content = []
    rating_floor = math.ceil(rating)
    num_golden = rating_floor
    num_empty = 5 - num_golden
    for _ in range(num_golden):
        rating_box_content.append(
            {
                "type": "icon",
                "size": "xs",
                "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png",
            }
        )
    for _ in range(num_empty):
        rating_box_content.append(
            {
                "type": "icon",
                "size": "xs",
                "url": "https://developers-resource.landpress.line.me/fx/img/review_gray_star_28.png",
            }
        )

    rating_box_content.append(
        {
            "type": "text",
            "text": str(rating),
            "size": "xs",
            "color": "#8c8c8c",
            "margin": "md",
            "flex": 0,
        }
    )
    card["body"]["contents"][1]["contents"] = rating_box_content
    return card


def generate_flex_message(place_details: list[dict]) -> dict:
    flex_message_template = {
        "type": "carousel",
        "contents": [],
    }

    for detail in place_details:
        flex_message_template["contents"].append(generate_card(**detail))

    return flex_message_template


def what_to_eat(latitude: str, longitude: str) -> dict:
    restaurants = get_food(latitude, longitude)
    if len(restaurants) == 0:
        return MESSAGE.NO_RESULT.value

    # Format the text
    place_details = []
    for restaurant in restaurants:
        place_detail = get_place_detail(latitude,longitude,restaurant)
        place_details.append(place_detail)

    flex_message_dict = generate_flex_message(place_details)

    return flex_message_dict


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
