import time

import numpy as np

from miyanmaayeh.action import ActionType, AgentAction, MarketAction
from miyanmaayeh.history import AgentHistory, MarketHistory


class Agent:
    def __init__(self, confidence_level, production, inventory, income, cash):
        self.confidence_level = confidence_level
        self.noise_generator = np.random.default_rng(time.time())
        self.ng_std = (1 - self.confidence_level) / 6
        self.production = production
        self.inventory = inventory
        self.wage = income
        self.cash = cash
        self.history = []

    def tick(self):
        self.cash += self.income
        self.inventory += self.production

    def apply_perception_on_market_prices(self, market_price_history):
        sz = len(market_price_history)
        noise = self.noise_generator.normal(loc=1, scale=self.ng_std, size=sz)
        market_prices = np.array(market_price_history)
        return (noise * market_prices).tolist()

    def analyze(self, market_history) -> MarketAction:
        return MarketAction(action_type=ActionType.skip.value, amount=0, bid=0, agent=self)

    def get_action(self, market_history) -> MarketAction:
        market_price_history = [item.price_equilibrium for item in market_history]
        market_price_history = self.apply_perception_on_market_prices(market_price_history)

        perceived_market_history = [
            MarketHistory(price, item.sell_action_count, item.buy_action_count) for price, item in zip(market_price_history, market_history)
        ]

        result = self.analyze(perceived_market_history)

        if result.type != ActionType.skip.value:
            assert result.bid != 0

        if result.type == ActionType.Buy.value:
            available_money = int(self.confidence_level * self.cash)
            result.amount = available_money // result.bid
        elif result.type == ActionType.Sell.value:
            result.amount = int(self.confidence_level * self.inventory)

        history = AgentHistory(type=result.type, bid=result.bid)
        self.history.append(history)

        return result

    def apply_action(self, action: AgentAction):
        pass
