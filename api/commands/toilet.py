import csv
import math
import re
import textwrap
from datetime import datetime, timedelta
from enum import Enum
from functools import cache
from pathlib import Path

from api.utils.configs import LANGUAGE


class GoogleMapSession:
    timeout = 5

    def __init__(self):
        self.last_update_time = datetime.now() - timedelta(days=1)

    def update_time(self):
        self.last_update_time = datetime.now()

    def is_expired(self) -> bool:
        expired_time = self.last_update_time + timedelta(
            minutes=self.timeout
        )
        if datetime.now() > expired_time:
            return True
        return False

    def set_expired(self):
        self.last_update_time = datetime.now() - timedelta(days=1)


GOOGLE_MAP_SESSION = GoogleMapSession()


class MessageEN(str, Enum):
    START_REPLY = "Please share your location to me"
    STOP_REPLY = "Stop session. Please start again if you want to search toilet"
    NO_RESULT = "No result in nearby location."


class MessageZHTW(str, Enum):
    START_REPLY = "請分享你的位置資訊給我"
    STOP_REPLY = "關閉對話。如果您想繼續搜尋，請重新開始對話"
    NO_RESULT = "找不到結果"


MESSAGE = MessageZHTW if LANGUAGE == "zh_TW" else MessageEN


@cache
def read_toilet_data() -> list[dict]:
    """Read toilet data"""
    toilet_data = []
    with (Path(__file__).parent / "data" / "toilet.csv").open(
        "r", encoding="utf-8", newline=""
    ) as filep:
        rows = csv.DictReader(filep)

        for row in rows:
            # remove \u3000 space
            for key in row:
                row[key]=row[key].replace("\u3000","")
            toilet_data.append(row)

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


def print_help() -> str:
    usage_en = textwrap.dedent(
        """
        * Start a new session to find toilet nearby.

        Example:
        @LineGPT toilet start

        * Stop a current session to use other location function.

        Example:
        @LineGPT toilet stop
        """
    )

    usage_zh_TW = textwrap.dedent(
        """
        * 開啟對話來尋找附近的廁所

        Example: 
        @LineGPT toilet start

        * 關閉目前對話來使用其他定位功能

        Example:
        @LineGPT toilet stop
        """
    )
    if LANGUAGE == "zh_TW":
        return usage_zh_TW
    return usage_en


def handle_message(message: str) -> str:
    if "help" in message:
        return print_help()

    if mrx := re.search(r"^toilet\s+(\w+)", message):
        match mrx.group(1):
            case "start":
                GOOGLE_MAP_SESSION.update_time()
                return MESSAGE.START_REPLY.value
            case "stop":
                GOOGLE_MAP_SESSION.set_expired()
                return MESSAGE.STOP_REPLY.value
            case _:
                return print_help()

    return print_help()
