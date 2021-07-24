from miyanmaayeh.action import ActionType


class Market:
    def __init__(self) -> None:
        self.initial_price = 1000
        self.history = []
        self.actions = []

    def new_tick(self):
        self.actions = []

    def calculate_market_price_equilibrium(self):
        sorted_actions = sorted(self.actions, key=lambda x: -x.bid if x.type == ActionType.Buy.value else x.bid)
        qs = 0
        qd = 0
        best_q = -1
        price_equilibrium = -1
        for action in sorted_actions:
            if action.type == ActionType.Buy.value:
                qd += action.amount
            elif action.type == ActionType.Sell.value:
                qs += action.amount

            if min(qs, qd) > best_q:
                best_q = min(qs, qd)
                price_equilibrium = action.bid

        return price_equilibrium

    def calculate_market_price(self):
        # apply regualtions here
        price_equilibrium = self.calculate_market_price_equilibrium()
        return price_equilibrium
