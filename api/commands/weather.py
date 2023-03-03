from collections import defaultdict
from enum import Enum
from typing import Optional, Tuple
from urllib import parse

import requests
from jinja2 import Template

from api.commands.base import Command
from api.utils.configs import LANGUAGE, WEATHER_TOKEN
from api.utils.info import Error, Warning

REPORT: Template = Template(
    """
{{ startTime }} - {{ endTime }}
{{Wx}}
降雨機率: {{PoP}} %
{{CI}}
最高溫: {{MaxT}} °C
最低溫: {{MinT}} °C""",
    trim_blocks=True,
)


class MessageEN(Enum):
    WEATHER_HEADING = "Weather forecast in 36 hours:"
    UNAVAILABLE_LOCATION = "Unavailable location"
    GET_DATA_FAILED = "Failed to get data"
    CANNOT_WORK_COLD = "It's too cold to work tokday"
    CANNOT_WORK_HOT = "It's too hot to work tokday"
    CANNOT_WORK_RAIN = "It will rain cats and dogs. Better not leave you house."
    REMIND_UMBRELLA = "It may rain today. Bring an umbrella with you."


class MessageZH(Enum):
    WEATHER_HEADING = "未來36小時天氣預報:"
    UNAVAILABLE_LOCATION = "該地區不適用"
    GET_DATA_FAILED = "獲取資料失敗"
    CANNOT_WORK_COLD = "今天太冷，不要去上班比較好，會凍死在路上"
    CANNOT_WORK_HOT = "今天太熱，不要去上班比較好，會熱死在路上"
    CANNOT_WORK_RAIN = "明天可能會下大雨，不要去上班比較好，太危險了"
    REMIND_UMBRELLA = "今天可能會下雨，出門記得帶傘"


MESSAGE = MessageEN if LANGUAGE == "en" else MessageZH


class WeatherCommand(Command):
    available_location = [
        "宜蘭縣",
        "花蓮縣",
        "臺東縣",
        "澎湖縣",
        "金門縣",
        "連江縣",
        "臺北市",
        "新北市",
        "桃園市",
        "臺中市",
        "臺南市",
        "高雄市",
        "基隆市",
        "新竹縣",
        "新竹市",
        "苗栗縣",
        "彰化縣",
        "南投縣",
        "雲林縣",
        "嘉義縣",
        "嘉義市",
        "屏東縣",
    ]
    usage_en = """* Check for the weather in the next 36 hours
@LineGPT weather <location>

Example:
@LineGPT weather 嘉義縣
        """
    usage_zh = """* 查詢未來36小時的天氣預報
@LineGPT weather <地點>

Example:
@LineGPT weather 嘉義縣
        """

    def __init__(
        self, subcommand: Optional[str] = None, args: Optional[str] = None
    ) -> None:
        super().__init__(subcommand, args)
        self.location = self.args

    def execute(self, **kwargs):
        if self.location not in self.available_location:
            return Error(MESSAGE.UNAVAILABLE_LOCATION.value)
        data = requests.get(
            (
                "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
                f"?Authorization={WEATHER_TOKEN}"
                "&format=JSON"
                f"&locationName={parse.quote(self.location)}"
            )
        ).json()

        if data["success"] != "true":
            return Warning(MESSAGE.GET_DATA_FAILED.value)

        data_dict = defaultdict(list)
        for el in data["records"]["location"][0]["weatherElement"]:
            for time in el["time"]:
                data_dict[el["elementName"]].append(time["parameter"]["parameterName"])
        for time in data["records"]["location"][0]["weatherElement"][0]["time"]:
            data_dict["startTime"].append(time["startTime"])
            data_dict["endTime"].append(time["endTime"])

        message = []
        if int(min(data_dict["MinT"])) < 15:
            message.append(MESSAGE.CANNOT_WORK_COLD.value)

        if int(max(data_dict["MaxT"])) > 30:
            message.append(MESSAGE.CANNOT_WORK_HOT.value)

        if 100 > int(min(data_dict["PoP"])) > 60:
            message.append(MESSAGE.REMIND_UMBRELLA.value)

        if int(min(data_dict["PoP"])) == 100:
            message.append(MESSAGE.CANNOT_WORK_RAIN.value)

        report_list = []
        for i in range(3):
            report_data = {}
            for key in data_dict:
                report_data[key] = data_dict[key][i]
            report_list.append(REPORT.render(report_data))

        return (
            MESSAGE.WEATHER_HEADING.value
            + "\n"
            + "\n".join(report_list)
            + "\n\n"
            + ",".join(message)
        )


def parse_args(args_msg: str) -> Tuple[str, str]:
    args = args_msg.strip()
    return None, args
