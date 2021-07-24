from enum import Enum


class ActionType(Enum):
    Buy = "buy"
    Sell = "sell"
    skip = "skip"


class AgentAction:
    def __init__(self, action_type, amount, bid) -> None:
        self.type = action_type
        self.amount = amount
        self.bid = bid


class MarketAction:
    def __init__(self, action_type, amount, bid, agent) -> None:
        self.type = action_type
        self.amount = amount
        self.bid = bid
        self.agent = agent
