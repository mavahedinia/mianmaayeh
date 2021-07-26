import time

import numpy as np

from miyanmaayeh.action import ActionType, AgentAction, MarketAction
from miyanmaayeh.history import AgentHistory, MarketHistory


class Agent:
    def __init__(self, confidence_level, production, inventory, income, cash):
        self.confidence_level = confidence_level
        self.noise_generator = np.random.default_rng(int(time.time() * 10000))
        self.ng_std = (1 - self.confidence_level) / 6
        self.production = production
        self.inventory = inventory
        self.income = income
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

    def analyze(self, market_history: MarketHistory) -> MarketAction:
        return MarketAction(action_type=ActionType.Skip.value, amount=0, bid=0, agent=self)

    def get_action(self, market_history) -> MarketAction:
        market_price_history = [item.price_equilibrium for item in market_history]
        market_price_history = self.apply_perception_on_market_prices(market_price_history)

        perceived_market_history = [
            MarketHistory(
                price_equilibrium=price, sell_actions=item.sell_action_count, buy_actions=item.buy_action_count, volume=item.volume
            )
            for price, item in zip(market_price_history, market_history)
        ]

        result = self.analyze(perceived_market_history)

        if result.type != ActionType.Skip.value:
            assert result.bid != 0

        if result.type == ActionType.Buy.value:
            available_money = int(self.confidence_level * self.cash)
            result.amount = available_money // result.bid
        elif result.type == ActionType.Sell.value:
            result.amount = int(self.confidence_level * self.inventory)

        if result.amount <= 0:
            result.type = ActionType.Skip.value
            result.amount = 0
            result.bid = 0

        history = AgentHistory(action_type=result.type, bid=result.bid)
        self.history.append(history)

        return result

    def apply_action(self, action: AgentAction):
        if action.type == ActionType.Buy.value:
            self.inventory += action.amount
            self.cash -= action.price * action.amount
        elif action.type == ActionType.Sell.value:
            self.inventory -= action.amount
            self.cash += action.price * action.amount


class FundamentalistAgent(Agent):
    def analyze(self, market_history: MarketHistory):
        market_indicator = np.random.rand(1) * 3
        bid = np.random.uniform(50, 100)
        if len(market_history) > 0:
            bid = market_history[-1].price_equilibrium

        if market_indicator > 2:
            return MarketAction(
                action_type=ActionType.Buy.value,
                agent=self,
                amount=0,
                bid=bid,
            )
        elif market_indicator > 1:
            return MarketAction(
                action_type=ActionType.Skip.value,
                agent=self,
                amount=0,
                bid=0,
            )
        return MarketAction(
            action_type=ActionType.Sell.value,
            agent=self,
            amount=0,
            bid=bid,
        )


class ContrarianAgent(Agent):
    EPS = 0.05

    def analyze(self, market_history: MarketHistory) -> MarketAction:
        if len(market_history) > 0:
            total_actions = market_history[-1].buy_action_count + market_history[-1].sell_action_count
            market_indicator = (market_history[-1].buy_action_count - market_history[-1].sell_action_count) / total_actions
            bid = market_history[-1].price_equilibrium
        else:
            market_indicator = np.random.uniform(-2, 2)
            bid = np.random.uniform(50, 100)

        if market_indicator > self.EPS:
            return MarketAction(
                ActionType.Sell.value,
                agent=self,
                amount=0,
                bid=bid,
            )
        elif market_indicator < -self.EPS:
            return MarketAction(
                ActionType.Buy.value,
                agent=self,
                amount=0,
                bid=bid,
            )
        return MarketAction(
            ActionType.Skip.value,
            agent=self,
            amount=0,
            bid=0,
        )


class TechnicalAnalystAgent(Agent):
    EPS = 0.05

    @staticmethod
    def ewma_vectorized(data, alpha, offset=None, dtype=None, order="C", out=None):
        data = np.array(data, copy=False)
        if dtype is None:
            if data.dtype == np.float32:
                dtype = np.float32
            else:
                dtype = np.float64
        else:
            dtype = np.dtype(dtype)

        if data.ndim > 1:
            data = data.reshape(-1, order)
        if out is None:
            out = np.empty_like(data, dtype=dtype)
        else:
            assert out.shape == data.shape
            assert out.dtype == dtype
        if data.size < 1:
            return out

        if offset is None:
            offset = data[0]

        alpha = np.array(alpha, copy=False).astype(dtype, copy=False)
        scaling_factors = np.power(1.0 - alpha, np.arange(data.size + 1, dtype=dtype), dtype=dtype)
        np.multiply(data, (alpha * scaling_factors[-2]) / scaling_factors[:-1], dtype=dtype, out=out)
        np.cumsum(out, dtype=dtype, out=out)
        out /= scaling_factors[-2::-1]
        if offset != 0:
            offset = np.array(offset, copy=False).astype(dtype, copy=False)
            out += offset * scaling_factors[1:]
        return out

    def analyze(self, market_history: MarketHistory) -> MarketAction:

        if len(market_history) > 0:
            prices_list = [item.price_equilibrium for item in market_history]
            ewma_12_days = self.ewma_vectorized(prices_list, 2 / (12 + 1))
            ewma_26_days = self.ewma_vectorized(prices_list, 2 / (26 + 1))
            MACD_ind = (ewma_12_days - ewma_26_days)[-1]

            bid = market_history[-1].price_equilibrium
        else:
            MACD_ind = np.random.uniform(-1, 1)
            bid = np.random.uniform(50, 100)

        if MACD_ind > self.EPS:
            return MarketAction(
                ActionType.Buy.value,
                agent=self,
                amount=0,
                bid=bid,
            )
        elif MACD_ind < -self.EPS:
            return MarketAction(
                ActionType.Sell.value,
                agent=self,
                amount=0,
                bid=bid,
            )
        return MarketAction(
            ActionType.Skip.value,
            agent=self,
            amount=0,
            bid=0,
        )
