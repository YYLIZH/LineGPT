from api.commands.weather import WeatherCommand


def test_weather_command():
    command = WeatherCommand(args="新竹市")
    result = command.execute()
    assert str(result).startswith("Weather forecast in 36 hours:") or str(
        result
    ).startswith("未來36小時天氣預報:")


def test_no_area():
    command = WeatherCommand(args="遠得要命王國")
    result = command.execute()
    assert str(result) == "Error: Unavailable location" or str(result) == "錯誤: 該地區不適用"


def test_help():
    command = WeatherCommand()
    result = command.print_usage()
    assert result == WeatherCommand.usage_en or result == WeatherCommand.usage_zh_TW
