class MarketHistory:
    def __init__(self, price_equilibrium, sell_actions, buy_actions) -> None:
        self.price_equilibrium = price_equilibrium
        self.sell_action_count = sell_actions
        self.buy_action_count = buy_actions


class AgentHistory:
    def __init__(self, type, bid) -> None:
        self.type = type
        self.bid = bid
