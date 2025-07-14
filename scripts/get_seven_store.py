import json
import random
import time
import xml.etree.ElementTree as ET

import requests

AREA_CODE = {
    "台北市": "01",
    "基隆市": "02",
    "新北市": "03",
    "桃園市": "04",
    "新竹市": "05",
    "新竹縣": "06",
    "苗栗縣": "07",
    "台中市": "08",
    "台中縣": "09",
    "彰化縣": "10",
    "南投縣": "11",
    "雲林縣": "12",
    "嘉義市": "13",
    "嘉義縣": "14",
    "台南市": "15",
    "台南縣": "16",
    "高雄市": "17",
    "高雄縣": "18",
    "屏東縣": "19",
    "宜蘭縣": "20",
    "花蓮縣": "21",
    "台東縣": "22",
    "澎湖縣": "23",
    "金門縣": "25",
    "連江縣": "24",
}


def get_town_list(city_id: str) -> list[str]:

    url = "https://emap.pcsc.com.tw/EMapSDK.aspx"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5,de-DE;q=0.4,de;q=0.3,zh-CN;q=0.2",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://emap.pcsc.com.tw",
        "Pragma": "no-cache",
        "Referer": "https://emap.pcsc.com.tw/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
    }

    data = {
        "commandid": "GetTown",
        "cityid": city_id,
        "leftMenuChecked": "",
    }
    response = requests.post(url, headers=headers, data=data)

    result = []
    root = ET.fromstring(response.text)
    for child in root.findall("GeoPosition"):
        tag = child.find("TownName")
        result.append(tag.text)
    return result


def get_shop_list(city: str, town: str):
    url = "https://emap.pcsc.com.tw/EMapSDK.aspx"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5,de-DE;q=0.4,de;q=0.3,zh-CN;q=0.2",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://emap.pcsc.com.tw",
        "Pragma": "no-cache",
        "Referer": "https://emap.pcsc.com.tw/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = {
        "commandid": "SearchStore",
        "city": city,
        "town": town,
        "roadname": "",
        "ID": "",
        "StoreName": "",
        "SpecialStore_Kind": "",
        "leftMenuChecked": "",
        "address": "",
    }

    response = requests.post(url, headers=headers, data=data)
    result = []
    root = ET.fromstring(response.text)
    for child in root.findall("GeoPosition"):
        name_tag = child.find("POIName")
        address_tag = child.find("Address")
        longitude_tag = child.find("X")
        latitude_tag = child.find("Y")

        if (
            name_tag is not None
            and address_tag is not None
            and longitude_tag is not None
            and latitude_tag is not None
        ):
            result.append(
                {
                    "name": f"{name_tag.text}店",
                    "address": address_tag.text,
                    "longitude": round(
                        float(longitude_tag.text) / 1000000, 4
                    ),
                    "latitude": round(
                        float(latitude_tag.text) / 1000000, 4
                    ),
                }
            )
    return result


def main():
    result = []
    for city, city_id in AREA_CODE.items():
        for town in get_town_list(city_id):
            result.extend(get_shop_list(city, town))
            time.sleep(random.uniform(1.1, 1.9))

        print(f"Grab {city} done.")
        time.sleep(random.randint(1, 10))

    with open("seven.json", "w", encoding="utf-8") as filep:
        json.dump(result, filep, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
