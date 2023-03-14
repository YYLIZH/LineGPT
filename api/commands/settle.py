from __future__ import annotations
import re
import typing

from api.commands.base import Command
from api.utils.configs import LANGUAGE


class SettleCommand(Command):
    usage_en = """* Settle the money transaction
@LineGPT settle
<chart>

Example:
@LineGPT settle
Iron man: 100
Batman: 300
Superman: 240
Spiderman: 0

Here is the result:
Spiderman -> Batman 140.0
Iron man -> Superman 60.0
Spiderman -> Superman 20.0
"""

    usage_zh_TW = """* 多人分帳
@LineGPT settle
<chart>

Example:
@LineGPT settle
大壯: 100
小帥: 300
小美: 240
大黑: 0

以下是分帳結果：
大黑 -> 小帥 140.0
大壯 -> 小美 60.0
大黑 -> 小美 20.0
"""

    def __init__(
        self, subcommand: typing.Optional[str] = None, args: typing.Optional[str] = None
    ) -> None:
        args = args.replace("：", ":")  # Replace chinese full colon
        super().__init__(subcommand, args)
        self.expenses = {}

    @classmethod
    def setup(cls, args_msg: str) -> SettleCommand:
        args = args_msg.lstrip()
        return cls(None, args)

    def execute(self, **kwargs):
        self.parse_expense()
        transactions = self.settle_money()
        heading = "Here is the result:\n" if LANGUAGE == "en" else "以下是分帳結果：\n"

        return heading + "\n".join(
            [
                f"{transaction[0]} -> {transaction[1]} {transaction[2]}"
                for transaction in transactions
            ]
        )

    def parse_expense(self):
        pattern = re.compile(r"(.+): *(\d+)")
        for line in self.args.split("\n"):
            if mrx := pattern.search(line):
                self.expenses[mrx.group(1)] = int(mrx.group(2))

    def settle_money(self):
        """
        Calculates the amount each person owes or is owed after settling expenses.

        Arguments:
        expenses -- a dictionary of the form {person: amount_paid} representing the expenses paid by each person

        Returns:
        A list of tuples representing the money transactions needed to settle the expenses.
        """
        total_expenses = sum(self.expenses.values())
        num_people = len(self.expenses)
        average_expense = total_expenses / num_people
        owed = {
            person: amount_paid - average_expense
            for person, amount_paid in self.expenses.items()
        }

        transactions = []
        while any(owed.values()):
            person1, amount1 = max(owed.items(), key=lambda x: x[1])
            person2, amount2 = min(owed.items(), key=lambda x: x[1])
            amount = min(-amount2, amount1)
            transactions.append((person2, person1, amount))
            owed[person1] -= amount
            owed[person2] += amount

        return transactions
