import csv
import json
import math
import re
import textwrap
from enum import Enum
from functools import cache
from pathlib import Path

from linebot.v3.messaging import (
    FlexContainer,
    FlexMessage,
    TextMessage,
)
from linebot.v3.webhooks import LocationMessageContent

from api.commands.googlemap import GOOGLE_MAP_SESSION
from api.utils.configs import LANGUAGE


class MessageEN(str, Enum):
    NO_RESULT = "No result in nearby location."


class MessageZHTW(str, Enum):
    NO_RESULT = "找不到結果"


MESSAGE = MessageZHTW if LANGUAGE == "zh_TW" else MessageEN


@cache
def read_toilet_data() -> list[dict]:
    """Read toilet data"""
    toilet_data = []
    data_dir = Path(__file__).parent / "data"

    # Read public toilet
    with (data_dir / "toilet.csv").open(
        "r", encoding="utf-8", newline=""
    ) as filep:
        rows = csv.DictReader(filep)

        for row in rows:
            # remove \u3000 space
            for key in row:
                row[key] = row[key].replace("\u3000", "")
            toilet_data.append(
                {
                    "name": row["name"],
                    "address": row["address"],
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                }
            )

    # Read fami toilet
    with (data_dir / "fami.json").open(
        "r", encoding="utf-8"
    ) as filep:
        fami = json.load(filep)
        for item in fami:
            toilet_data.append(
                {
                    "name": item["NAME"],
                    "address": item["addr"],
                    "latitude": item["py"],
                    "longitude": item["px"],
                }
            )

    # Read seven toilet
    with (data_dir / "seven.json").open(
        "r", encoding="utf-8"
    ) as filep:
        seven = json.load(filep)
        toilet_data.extend(seven)

    return toilet_data


def get_toilets(
    latitude: str, longitude: str
) -> list[tuple[float, dict]]:
    toilet_data = read_toilet_data()
    distances_out = []

    for data in toilet_data:
        toilet, distance = curr2toilet((latitude, longitude), data)
        distances_out.append((distance, toilet))

    distances_out.sort(key=lambda item: item[0])
    return distances_out[:10]


def create_map_link(latitude: str, longitude: str) -> str:
    map_link = f"https://www.google.com/maps/search/?api=1&query={latitude}%2C{longitude}"
    return map_link


def calculate_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Use Haversine Formula

    Returns:
        The return value unit is km.

    """
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
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 距離（公里）
    distance = R * c

    return distance


def curr2toilet(
    curr_location: tuple[float, float], toilet: dict
) -> tuple[dict, float]:
    distance = calculate_distance(
        float(curr_location[0]),
        float(curr_location[1]),
        float(toilet["latitude"]),
        float(toilet["longitude"]),
    )
    return toilet, distance


def get_place_detail(toilet_calculation: tuple[float, dict]):
    distance, toilet_info = toilet_calculation
    return {
        "name": toilet_info["name"],
        "address": toilet_info["address"],
        "distance": f"{int(distance*1000)} m",
        "map_url": create_map_link(
            toilet_info["latitude"], toilet_info["longitude"]
        ),
    }


def generate_card(
    name: str,
    address: str,
    distance: float,
    map_url: str,
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
                        },
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
    return card


def generate_flex_message(place_details: list[dict]) -> dict:
    flex_message_template = {
        "type": "carousel",
        "contents": [],
    }

    for detail in place_details:
        flex_message_template["contents"].append(
            generate_card(**detail)
        )

    return flex_message_template


def where_to_pee(latitude: str, longitude: str) -> dict:
    toilets = get_toilets(latitude, longitude)
    if len(toilets) == 0:
        return MESSAGE.NO_RESULT.value

    # Format the message
    place_details = []
    for toilet in toilets:
        place_detail = get_place_detail(toilet_calculation=toilet)
        place_details.append(place_detail)

    flex_message_dict = generate_flex_message(place_details)
    return flex_message_dict


def generate_button() -> dict:
    template = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://line-gpt.vercel.app/static/toilet.png",
            "size": "full",
            "aspectRatio": "20:17",
            "aspectMode": "cover",
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": "Click and share your location. We will find the first 10 nearest place for you.",
                            "wrap": True,
                        }
                    ],
                }
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "Find toilet",
                        "uri": "https://line.me/R/nv/location/",
                    },
                }
            ],
            "flex": 0,
        },
    }
    return template


def print_help() -> str:
    usage_en = textwrap.dedent(
        """
        * Find toilet nearby.

        Example:
        @LineGPT toilet
        """
    )

    usage_zh_TW = textwrap.dedent(
        """
        * 尋找附近的廁所

        Example: 
        @LineGPT toilet
        """
    )
    if LANGUAGE == "zh_TW":
        return usage_zh_TW
    return usage_en


def handle_message(message: str) -> list[TextMessage]:
    if "help" in message:
        return [TextMessage(text=print_help())]

    if re.search(r"^toilet", message):
        GOOGLE_MAP_SESSION.set_app("toilet")
        return [
            FlexMessage(
                altText="toilet help",
                contents=FlexContainer.from_dict(generate_button()),
            )
        ]

    return [TextMessage(text=print_help())]


def handle_location_message(location_message: LocationMessageContent):
    result = where_to_pee(
        latitude=location_message.latitude,
        longitude=location_message.longitude,
    )
    messages = [
        FlexMessage(
            altText="toilet cards",
            contents=FlexContainer.from_dict(result),
        )
    ]
    return messages
