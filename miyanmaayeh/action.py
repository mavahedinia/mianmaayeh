from enum import Enum


class ActionType(Enum):
    Buy = "buy"
    Sell = "sell"
    Skip = "skip"


class AgentAction:
    def __init__(self, action_type, amount, price) -> None:
        self.type = action_type
        self.amount = amount
        self.price = price

    def __str__(self):
        return f"{self.type} - {self.amount} - {self.price}"


class MarketAction:
    def __init__(self, action_type, amount, bid, agent) -> None:
        self.type = action_type
        self.amount = amount
        self.bid = bid
        self.agent = agent

    def __repr__(self):
        return f"{self.type} - {self.amount} - {self.bid} - {self.agent}"
