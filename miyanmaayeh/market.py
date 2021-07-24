from copy import deepcopy

from miyanmaayeh.action import ActionType, AgentAction, MarketAction
from miyanmaayeh.history import MarketHistory


class Market:
    def __init__(self, initial_price=1000) -> None:
        self.initial_price = initial_price
        self.history = []
        self.actions = []

    def new_tick(self):
        self.actions = []

    def get_history(self):
        return self.history[-10:]

    def add_action(self, action: MarketAction):
        self.actions.append(action)

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
        actions_copy = deepcopy(self.actions)
        sell_actions = []
        buy_actions = []

        for action in actions_copy:
            if action.type == ActionType.Buy.value:
                buy_actions.append(action)
            elif action.type == ActionType.Sell.value:
                sell_actions.append(action)

        sell_actions = sorted(sell_actions, key=lambda x: x.bid)
        buy_actions = sorted(buy_actions, key=lambda x: -x.bid)

        market_price = self.calculate_market_price()
        market_q = 0

        history = MarketHistory(market_price, len(sell_actions), len(buy_actions), 0)

        sell_action_idx = 0
        buy_action_idx = 0

        while True:
            if sell_action_idx >= len(sell_actions):
                break
            if buy_action_idx >= len(buy_actions):
                break
            if sell_actions[sell_action_idx].bid > market_price or buy_actions[buy_action_idx].bid < market_price:
                break

            amount = min(sell_actions[sell_action_idx].amount, buy_actions[buy_action_idx].amount)
            market_q += amount

            buyer_agent_action = AgentAction(
                action_type=ActionType.Buy.value,
                amount=amount,
                price=market_price,
            )
            buy_actions[buy_action_idx].agent.apply_action(buyer_agent_action)

            seller_agent_action = AgentAction(
                action_type=ActionType.Sell.value,
                amount=amount,
                price=market_price,
            )
            sell_actions[sell_action_idx].agent.apply_action(seller_agent_action)

            buy_actions[buy_action_idx].amount -= amount
            sell_actions[sell_action_idx].amount -= amount

            if buy_actions[buy_action_idx].amount >= sell_actions[sell_action_idx].amount:
                sell_action_idx += 1
            else:
                buy_action_idx += 1

        history.volume = market_q
        self.history.append(history)
