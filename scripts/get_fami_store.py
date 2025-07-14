import json
import random
import time

import requests

CITIES = [
    "基隆市",
    "台北市",
    "新北市",
    "桃園市",
    "新竹市",
    "新竹縣",
    "苗栗縣",
    "台中市",
    "彰化縣",
    "南投縣",
    "雲林縣",
    "嘉義市",
    "嘉義縣",
    "台南市",
    "高雄市",
    "屏東縣",
    "宜蘭縣",
    "花蓮縣",
    "台東縣",
    "澎湖縣",
    "金門縣",
    "連江縣",
]


def get_town_list(city: str) -> dict:
    url = f"https://api.map.com.tw/net/familyShop.aspx?searchType=ShowTownList&type=toilet&city={city}&fun=setArea&key=6F30E8BF706D653965BDE302661D1241F8BE9EBC"

    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5,de-DE;q=0.4,de;q=0.3,zh-CN;q=0.2",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Referer": "https://www.family.com.tw/",
        "Sec-Fetch-Dest": "script",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Storage-Access": "active",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    }

    response = requests.get(url, headers=headers)

    return json.loads(
        response.text.replace("\r\n", "")
        .replace("setArea(", "")
        .rstrip(")")
        .strip()
        .replace(" ", "")
    )


def get_shop_list(city: str, town: str) -> dict:
    url = f"https://api.map.com.tw/net/familyShop.aspx?searchType=ShopList&type=toilet&city={city}&area={town}&road=&fun=setRoad&key=6F30E8BF706D653965BDE302661D1241F8BE9EBC"
    headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5,de-DE;q=0.4,de;q=0.3,zh-CN;q=0.2",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Referer": "https://www.family.com.tw/",
        "Sec-Fetch-Dest": "script",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Storage-Access": "active",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    }

    response = requests.get(url, headers=headers)
    return json.loads(
        response.text.replace("\r\n", "")
        .replace("setRoad(", "")
        .rstrip(")")
        .strip()
        .replace(" ", "")
    )


def main():
    result = []
    for city in CITIES:
        town_list = get_town_list(city)
        for town in town_list:
            try:
                result.extend(get_shop_list(city, town["town"]))
            except Exception:
                print(f"Fail to get data. City={city} Town={town}")
            time.sleep(random.uniform(1.1, 1.9))
        time.sleep(random.randint(1, 10))
        print(f"Grab {city} done.")

    with open("fami.json", "w", encoding="utf-8") as filep:
        json.dump(result, filep, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
