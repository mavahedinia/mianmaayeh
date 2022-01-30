from copy import deepcopy

from miyanmaayeh.action import ActionType, AgentAction, MarketAction
from miyanmaayeh.history import MarketHistory


class Market:
    def __init__(self, initial_price=1000, *args, **kwargs) -> None:
        self.initial_price = initial_price
        self.history = []
        self.actions = []

    def new_tick(self):
        self.actions = []

    def get_history(self):
        return self.history[-10:]

    def add_action(self, action: MarketAction):
        self.actions.append(action)

    def calculate_buy_price(self, market_price):
        return market_price

    def calculate_sell_price(self, market_price):
        return market_price

    def calculate_market_price_equilibrium(self):
        sorted_actions = sorted(self.actions, key=lambda x: -x.bid if x.type == ActionType.Buy.value else x.bid)
        qs = 0
        qd = 0
        best_q = 0
        price_equilibrium = 0
        for action in sorted_actions:
            if action.type == ActionType.Buy.value:
                qd += action.amount
            elif action.type == ActionType.Sell.value:
                qs += action.amount

            if min(qs, qd) > best_q:
                best_q = min(qs, qd)
                price_equilibrium = action.bid

        return max(1, price_equilibrium)

    def calculate_market_price(self):
        # apply price regualtions here
        price_equilibrium = self.calculate_market_price_equilibrium()
        return price_equilibrium

    def allocate_commodity(self):
        # apply allocation rule here
        sell_actions = []
        buy_actions = []

        for action in self.actions:
            new_action = MarketAction(action_type=action.type, amount=action.amount, bid=action.bid, agent=action.agent)
            if action.type == ActionType.Buy.value:
                buy_actions.append(new_action)
            elif action.type == ActionType.Sell.value:
                sell_actions.append(new_action)

        sell_actions = sorted(sell_actions, key=lambda x: x.bid)
        buy_actions = sorted(buy_actions, key=lambda x: -x.bid)

        market_price = self.calculate_market_price()
        market_q = 0
        market_profit = 0

        buyer_price = self.calculate_sell_price(market_price)
        seller_price = self.calculate_buy_price(market_price)

        history = MarketHistory(market_price, len(sell_actions), len(buy_actions), 0, 0)

        sell_action_idx = 0
        buy_action_idx = 0

        while True:
            if sell_action_idx >= len(sell_actions):
                break
            if buy_action_idx >= len(buy_actions):
                break
            if sell_actions[sell_action_idx].bid > buyer_price:
                break
            if buy_actions[buy_action_idx].bid < seller_price:
                break

            amount = min(sell_actions[sell_action_idx].amount, buy_actions[buy_action_idx].amount)
            market_q += amount
            market_profit += amount * abs(seller_price - buyer_price)

            buyer_agent_action = AgentAction(
                action_type=ActionType.Buy.value,
                amount=amount,
                price=buyer_price,
            )
            buy_actions[buy_action_idx].agent.apply_action(buyer_agent_action)

            seller_agent_action = AgentAction(
                action_type=ActionType.Sell.value,
                amount=amount,
                price=seller_price,
            )
            sell_actions[sell_action_idx].agent.apply_action(seller_agent_action)

            buy_actions[buy_action_idx].amount -= amount
            sell_actions[sell_action_idx].amount -= amount

            if buy_actions[buy_action_idx].amount >= sell_actions[sell_action_idx].amount:
                sell_action_idx += 1
            else:
                buy_action_idx += 1

        history.volume = market_q
        history.profit = market_profit
        self.history.append(history)


class MarketWithFriction(Market):
    EPS = 0.01

    def __init__(self, friction_rate, initial_price=1000, *args, **kwargs) -> None:
        self.friction_rate = friction_rate
        self.initial_price = initial_price
        self.history = []
        self.actions = []

    def calculate_buy_price(self, market_price):
        return market_price * (1 - self.friction_rate)

    def calculate_sell_price(self, market_price):
        return market_price

    def calculate_qs(self, market_price):
        q_s, q_d = 0, 0
        q_s_price = self.calculate_buy_price(market_price)
        q_d_price = self.calculate_sell_price(market_price)

        for action in self.actions:
            if action.type == ActionType.Buy.value and action.bid >= q_d_price:
                q_d += action.amount
            elif action.type == ActionType.Sell.value and action.bid <= q_s_price:
                q_s += action.amount

        return q_s, q_d

    def calculate_market_price(self):
        L, R = 0.01, 1e10

        while abs(R - L) >= self.EPS:
            mid = (L + R) / 2
            q_s, q_d = self.calculate_qs(mid)

            if q_s >= q_d:
                R = mid
            else:
                L = mid

        return L
