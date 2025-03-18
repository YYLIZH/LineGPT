from api.commands import print_usage
from unittest import mock
from . import line_handler

def test_print_usage(snapshot):
    help_message=print_usage()
    assert snapshot==help_message


def test_handle_message():
    res=line_handler.handle_message("aaa")
    assert res==print_usage()

    res=line_handler.handle_message("@LineGPT help")
    assert res==print_usage()

    res=line_handler.handle_message("@LineGPT gogo")
    assert res==print_usage()


def test_handle_message_eat(snapshot):
    assert snapshot==line_handler.handle_message("@LineGPT eat")

def test_handle_message_gpt(snapshot):
    assert snapshot==line_handler.handle_message("@LineGPT gpt")

def test_handle_message_settle(snapshot):
    assert snapshot==line_handler.handle_message("@LineGPT settle")

def test_handle_message_weather(snapshot):
    assert snapshot==line_handler.handle_message("@LineGPT weather")