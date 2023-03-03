from api.commands import print_usage
from api.commands.gpt import GptCommand
from api.commands.settle import SettleCommand
from api.commands.weather import WeatherCommand
from api.index import parse_message


def test_parse_message_help():
    command = parse_message("@LineGPT help ")
    assert command == print_usage()

    command = parse_message("@LineGPT")
    assert command == print_usage()


def test_parse_message_weather():
    command = parse_message("@LineGPT weather 新竹市")
    assert isinstance(command, WeatherCommand)
    assert command.subcommand is None
    assert command.args == "新竹市"

    command = parse_message("@LineGPT weather 新竹市 help")
    assert command == WeatherCommand.print_usage()

    command = parse_message("@LineGPT weather help")
    assert command == WeatherCommand.print_usage()


def test_parse_message_gpt():
    command = parse_message("@LineGPT gpt talk 你好")
    assert isinstance(command, GptCommand)
    assert command.subcommand == "talk"
    assert command.args == "你好"

    command = parse_message("@LineGPT gpt start")
    assert isinstance(command, GptCommand)
    assert command.subcommand == "start"
    assert command.args == None

    command = parse_message("@LineGPT gpt help ")
    assert command == GptCommand.print_usage()


def test_parse_message_settle():
    message = """@LineGPT settle
A: 400
B:100
C:  300
"""
    command = parse_message(message)
    assert isinstance(command, SettleCommand)
    assert command.subcommand == None
    assert command.args == "A: 400\nB:100\nC:  300"


def test_parse_message_no_such_command():
    command = parse_message("@LineGPT hakuna matata 555 888")
    assert command == "錯誤: No such command\n" + print_usage()
