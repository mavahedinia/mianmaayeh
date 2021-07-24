class MarketHistory:
    def __init__(self, price_equilibrium, sell_actions, buy_actions, volume) -> None:
        self.price_equilibrium = price_equilibrium
        self.sell_action_count = sell_actions
        self.buy_action_count = buy_actions
        self.volume = volume


class AgentHistory:
    def __init__(self, action_type, bid) -> None:
        self.type = action_type
        self.bid = bid
