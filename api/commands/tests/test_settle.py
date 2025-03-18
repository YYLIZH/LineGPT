import textwrap

from api.commands import settle

USER_MSG = textwrap.dedent(
    """
    settle
    Iron man: 100
    Batman:  300
    Superman: 240
    Spiderman:  0
    """
)


def test_parse_expense():
    assert settle.parse_expense(USER_MSG) == {
        "Iron man": 100,
        "Batman": 300,
        "Superman": 240,
        "Spiderman": 0,
    }


def test_settle_money():
    expense = {
        "Iron man": 100,
        "Batman": 300,
        "Superman": 240,
        "Spiderman": 0,
    }

    assert settle.settle_money(expense) == []


def test_settle_command():
    message = """Iron man: 100
Batman:  300
Superman: 240
Spiderman:  0
"""
    command = SettleCommand(args=message)
    result = command.execute()
    assert result == "\n".join(
        [
            "以下是分帳結果：",
            "Spiderman -> Batman 140.0",
            "Iron man -> Superman 60.0",
            "Spiderman -> Superman 20.0",
        ]
    )


def test_settle_command_full_colon():
    message = """Iron man: 100
Batman：  300
Superman: 240
Spiderman:  0
"""
    command = SettleCommand(args=message)
    result = command.execute()
    assert result == "\n".join(
        [
            "以下是分帳結果：",
            "Spiderman -> Batman 140.0",
            "Iron man -> Superman 60.0",
            "Spiderman -> Superman 20.0",
        ]
    )


def test_settle_command_cannot_full_divide():
    message = """Iron man: 100
Batman：  300
Superman: 240
"""
    command = SettleCommand(args=message)
    result = command.execute()
    assert result == "\n".join(
        [
            "以下是分帳結果：",
            "Iron man -> Batman 86.7",
            "Iron man -> Superman 26.7",
        ]
    )
