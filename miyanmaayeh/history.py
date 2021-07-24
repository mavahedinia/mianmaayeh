class RunHistory:
    def __init__(self, volume, sell_actions, buy_actions, price, wealth, demands=[], supplies=[]) -> None:
        self.volume = volume  # p * q
        self.sell_action_count = sell_actions
        self.buy_action_count = buy_actions
        self.price = price
        self.wealth = wealth  # liquidity + market_value*q for all agents
        self.demands = demands
        self.supplies = supplies


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
