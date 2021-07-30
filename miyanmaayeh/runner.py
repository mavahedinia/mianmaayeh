import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from tqdm import tqdm

from miyanmaayeh.action import ActionType
from miyanmaayeh.agent import (
    Agent,
    ContrarianAgent,
    CopyCatAgent,
    FundamentalistAgent,
    LongTermBuyerAgent,
    RandomAgent,
    TechnicalAnalystAgent,
)
from miyanmaayeh.history import RunHistory
from miyanmaayeh.market import Market


class Runner:
    def __init__(self, config) -> None:
        self.market = Market()
        self.agents = []
        self.history = []
        self.take_snapshots_in = config.get("snapshots_in")

        agents_config = config.get("agents-config", {})
        total_agents = config.get("total_agents", 0)
        fundamentalist_agent_count = int(total_agents * config.get("fundamentalist_count", 0))
        self.initialize_agents(FundamentalistAgent, fundamentalist_agent_count, agents_config)
        contrarian_agent_count = int(total_agents * config.get("contrarian_count", 0))
        self.initialize_agents(ContrarianAgent, contrarian_agent_count, agents_config)
        technical_analyst_agent_count = int(total_agents * config.get("technical_analyst_count", 0))
        self.initialize_agents(TechnicalAnalystAgent, technical_analyst_agent_count, agents_config)
        random_agent_count = int(total_agents * config.get("random_count", 0))
        self.initialize_agents(RandomAgent, random_agent_count, agents_config)
        long_term_buyer_agent_count = int(total_agents * config.get("long_term_buyer_count", 0))
        self.initialize_agents(LongTermBuyerAgent, long_term_buyer_agent_count, agents_config)
        copycat_agent_count = int(total_agents * config.get("copycat_count", 0))
        self.initialize_agents(CopyCatAgent, copycat_agent_count, agents_config)

        self.plot_dir = config.get("plot_dir")

    def initialize_agents(self, agent_cls: Agent, cnt, agents_config):
        for _ in range(cnt):
            confidence_level = np.random.normal(0.5, 0.5 / 2)
            if confidence_level > 0.9:
                confidence_level = 0.9
            if confidence_level < 0:
                confidence_level = 0

            production_avg = agents_config.get("production-average", 1000)
            production_std = agents_config.get("production-std", 200)
            producers_count = agents_config.get("producers-percentage", 20)
            production = np.random.normal(production_avg, production_std)
            is_producer = np.random.uniform(0, 100) <= producers_count
            if production < 0 or not is_producer:
                production = 0

            income_alpha = agents_config.get("income-alpha", 4)
            income_beta = agents_config.get("income-beta", 1500)
            income = np.random.gamma(income_alpha, income_beta)
            # if income < 1000:
            #     income = 1000

            agent = agent_cls(
                confidence_level=confidence_level,
                production=production,
                inventory=0,
                income=income,
                cash=0,
            )
            self.agents.append(agent)

    def run(self, ticks):
        for tick in tqdm(range(ticks)):
            self.market.new_tick()
            for agent in self.agents:
                agent.tick()

            self.run_iteration(tick)

            self.sort_agents_by_welfare()
            self.record_history(tick)

    def sort_agents_by_welfare(self):
        market_price = self.market.history[-1].price_equilibrium
        self.agents = sorted(self.agents, key=lambda x: (-market_price * x.inventory + x.cash) * (x.GROUP != "Copycat"))

    def run_iteration(self, tick):
        market_history = self.market.get_history()
        best_agents = self.agents[:10]

        for agent in self.agents:
            action = agent.get_action(market_history, best_agents=best_agents)
            self.market.add_action(action)

        self.market.allocate_commodity()

    def record_history(self, tick):
        market_price = self.market.history[-1].price_equilibrium
        # wealth = 0
        groups = set([item.GROUP for item in self.agents])
        wealth = {group: 0 for group in groups}
        for agent in self.agents:
            wealth[agent.GROUP] += agent.cash + agent.inventory * market_price

        history = RunHistory(
            volume=self.market.history[-1].volume,
            sell_actions=self.market.history[-1].sell_action_count,
            buy_actions=self.market.history[-1].buy_action_count,
            price=market_price,
            wealth=wealth,
        )

        if tick in self.take_snapshots_in:
            history.demands, history.supplies = self._extract_demand_supply()

        self.history.append(history)

    def _extract_demand_supply(self):
        actions = self.market.actions

        demand_actions = []
        supply_actions = []

        for action in actions:
            if action.type == ActionType.Buy.value:
                demand_actions.append(action)
            elif action.type == ActionType.Sell.value:
                supply_actions.append(action)

        demand_actions = sorted(demand_actions, key=lambda x: -x.bid)
        supply_actions = sorted(supply_actions, key=lambda x: x.bid)

        q_d = 0
        demand_series = []
        for demand in demand_actions:
            demand_series.append((demand.bid, q_d))
            q_d += demand.amount

        q_s = 0
        supply_series = []
        for supply in supply_actions:
            q_s += supply.amount
            supply_series.append((supply.bid, q_s))

        return demand_series, supply_series

    def generate_plot(self):
        sns.set_theme()

        self.generate_price_plot()
        self.generate_wealth_plot()
        self.generate_volume_plot()

        self.generate_demand_supply_facet()

    def generate_price_plot(self):
        prices = [item.price for item in self.history]
        ticks = np.arange(0, len(prices))

        z = np.polyfit(ticks, prices, 1)
        trendline_func = np.poly1d(z)
        trendline = [trendline_func(tick) for tick in ticks]

        plt.figure("Market Price", figsize=(12, 8))
        fig = sns.lineplot(x=ticks, y=prices)
        sns.lineplot(x=ticks, y=trendline, label="Trendline", color="green", legend="brief")

        fig.set(xlabel="Time", ylabel="Price", title="Market Price")

        plt.savefig(self.plot_dir + "prices.png")
        plt.close("Market Price")

    def generate_wealth_plot(self):
        wealth = [item.wealth for item in self.history]
        groups = set([item.GROUP for item in self.agents])

        plt.figure("Society Welfare")
        for group in groups:
            y = [item[group] for item in wealth]
            fig = sns.lineplot(x=np.arange(0, len(y)), y=y, label=group, legend="brief")
        fig.set(xlabel="Time", ylabel="Wealth", title="Society Welfare")

        plt.savefig(self.plot_dir + "welfare.png")
        plt.close("Society Welfare")

    def generate_volume_plot(self):
        volume = [item.volume for item in self.history]

        plt.figure("Market Volume")
        fig = sns.lineplot(x=np.arange(0, len(volume)), y=volume)
        fig.set(xlabel="Time", ylabel="Quantity", title="Market Volume")

        plt.savefig(self.plot_dir + "volume.png")
        plt.close("Market Volume")

    def generate_demand_supply_facet(self):
        for tick in self.take_snapshots_in:
            if tick >= len(self.history):
                break

            output_file = self.plot_dir + f"sd_{tick}"
            demands = self.history[tick].demands
            supplies = self.history[tick].supplies

            plt.figure(output_file)

            fig = sns.lineplot(x=[x[0] for x in demands], y=[x[1] for x in demands], legend="brief", label="Demand")
            sns.lineplot(x=[x[0] for x in supplies], y=[x[1] for x in supplies], label="Supply")

            fig.set(xlabel="Price", ylabel="Quantity", title=f"Supply - Demand plot at {tick}")

            plt.savefig(output_file)
            plt.close(output_file)
