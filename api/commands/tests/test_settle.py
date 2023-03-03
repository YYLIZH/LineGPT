from api.commands.settle import SettleCommand


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