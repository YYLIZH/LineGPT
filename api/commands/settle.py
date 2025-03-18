import re
import textwrap
from enum import Enum

from api.utils.configs import LANGUAGE


class MessageEN(str, Enum):
    HEADER = "Here is the result:"


class MessageZHTW(str, Enum):
    HEADER = "以下是分帳結果:"


MESSAGE = MessageZHTW if LANGUAGE == "zh_TW" else MessageEN


def parse_expense(expense_chart: str) -> dict:
    expenses = {}

    pattern = re.compile(r"(.+):\s*(\d+)")
    for line in expense_chart.splitlines():
        if mrx := pattern.search(line):
            expenses[mrx.group(1)] = int(mrx.group(2))

    return expenses


def settle_money(expenses: dict) -> list[tuple[str, str, float]]:
    """Settle money

    Calculates the amount each person owes or is owed after settling expenses.

    Args:
        expenses (dict): A dictionary of the form representing the expenses paid by each person.
            key: person
            value: paid money

    Returns:
        transactions (list(tuple)): A list of tuples representing the money transactions
            needed to settle the expenses. The meaning of each element will be

                        {ele[0]} need to give {ele[1]} {ele[2]} money
    """
    total_expenses = sum(expenses.values())
    num_people = len(expenses)
    average_expense = total_expenses / num_people
    owed = {
        person: amount_paid - average_expense
        for person, amount_paid in expenses.items()
    }

    transactions = []
    while any(map(lambda x: x > 1, owed.values())):
        person1, amount1 = max(owed.items(), key=lambda x: x[1])
        person2, amount2 = min(owed.items(), key=lambda x: x[1])
        amount = min(-amount2, amount1)
        transactions.append((person2, person1, amount))
        owed[person1] -= amount
        owed[person2] += amount

    return transactions


def print_help():
    usage_en = textwrap.dedent(
        """
            * Settle the money transaction
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
    )

    usage_zh_TW = textwrap.dedent(
        """
        * 多人分帳
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
    )
    if LANGUAGE == "zh_TW":
        return usage_zh_TW
    return usage_en


def handle_message(message: str) -> str:
    if "help" in message:
        return print_help()

    chart = message.replace("：", ":")  # Replace chinese full colon
    expenses = parse_expense(chart)
    transactions = settle_money(expenses)

    return MESSAGE.HEADER.value + "\n".join(
        [
            f"{transaction[0]} -> {transaction[1]} {round(transaction[2],1)}"
            for transaction in transactions
        ]
    )
