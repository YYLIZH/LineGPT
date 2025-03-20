from api.commands import weather
from api.utils.info import Error

def test_print_help(snapshot):
    assert snapshot == weather.print_help()


def test_handle_message_help():
    message = "weather help"
    assert weather.handle_message(message) == weather.print_help()


def test_handle_message():
    message = "weather 新竹市"
    result = weather.handle_message(message)
    assert result.startswith(
        "Weather forecast in 36 hours:"
    ) or result.startswith("未來36小時天氣預報:")


def test_no_area():
    message = "weather 遠得要命王國"
    result = weather.handle_message(message)
    assert result == str(Error(weather.MESSAGE.UNAVAILABLE_LOCATION))
