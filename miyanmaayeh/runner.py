import math
from pathlib import Path
from time import time

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
    VerificationAgent,
)
from miyanmaayeh.history import RunHistory
from miyanmaayeh.market import Market
from miyanmaayeh.utils import get_steady_state

agent_key_to_class = {
    "fundamentalist_count": FundamentalistAgent,
    "contrarian_count": ContrarianAgent,
    "technical_analyst_count": TechnicalAnalystAgent,
    "random_count": RandomAgent,
    "long_term_buyer_count": LongTermBuyerAgent,
    "copycat_count": CopyCatAgent,
    "verifier_count": VerificationAgent,
}


class Runner:
    def __init__(self, config) -> None:
        market_cls = config.get("market-class", Market)
        self.market_options = config.get("market-options", {})
        self.market = market_cls(**self.market_options)

        self.agents = []
        self.history = []
        self.take_snapshots_in = config.get("snapshots_in")

        self.agents_config = config.get("agents-config", {})
        initial_agents = config.get("initial_agents", 0)
        new_agents = config.get("new_agents", 0)
        avg_wait_time = config.get("average_time_to_add_agents", 0.0001)

        for agent_key in agent_key_to_class:
            agent_cls = agent_key_to_class[agent_key]
            agent_count = int(initial_agents * config.get(agent_key, 0))
            self.initialize_agents(agent_cls, agent_count, self.agents_config, [0] * agent_count)

            # Compose new agents
            agent_count = int(new_agents * config.get(agent_key, 0))
            activation_times = np.random.exponential(1 / avg_wait_time, size=agent_count)
            self.initialize_agents(agent_cls, agent_count, self.agents_config, activation_times)

        self.plot_dir = config.get("plot_dir", None)
        if self.plot_dir is not None:
            Path(self.plot_dir).mkdir(parents=True, exist_ok=True)

    def initialize_agents(self, agent_cls: Agent, cnt, agents_config, activation_times):
        np.random.seed(int(time()))
        for i in range(cnt):
            confidence_level = np.random.normal(0.5, 0.5 / 3)
            if confidence_level > 0.9:
                confidence_level = 0.9
            if confidence_level < 0.1:
                confidence_level = 0.1

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

            agent = agent_cls(
                confidence_level=confidence_level,
                production=production,
                inventory=agents_config.get("initial-inventory", 0),
                income=income,
                cash=agents_config.get("initial-cash", 0),
                activation_time=activation_times[i],
            )
            self.agents.append(agent)

    def run(self, ticks):
        for tick in tqdm(range(ticks)):
            self.market.new_tick()
            for agent in self.agents:
                agent.tick(tick)

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
            if not agent.is_active:
                continue

            action = agent.get_action(market_history, best_agents=best_agents)
            self.market.add_action(action)

        self.market.allocate_commodity()

    def record_history(self, tick):
        market_price = self.market.history[-1].price_equilibrium
        # wealth = 0
        groups = set([item.GROUP for item in self.agents])
        wealth = {group: 0 for group in groups}
        for agent in self.agents:
            if not agent.is_active:
                continue
            wealth[agent.GROUP] += agent.cash + agent.inventory * market_price

        history = RunHistory(
            volume=self.market.history[-1].volume,
            sell_actions=self.market.history[-1].sell_action_count,
            buy_actions=self.market.history[-1].buy_action_count,
            price=market_price,
            wealth=wealth,
            market_profit=self.market.history[-1].profit,
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
        if self.plot_dir is None:
            return

        sns.set_theme()

        self.generate_price_plot()
        self.generate_wealth_plot()
        self.generate_volume_plot()

        self.generate_demand_supply_facet()

        plt.close("all")

    def generate_price_plot(self):
        prices = [item.price for item in self.history]
        ticks = np.arange(0, len(prices))

        steady_ticks, steady_prices = get_steady_state(prices)

        z = np.polyfit(steady_ticks, steady_prices, 1)
        trendline_func = np.poly1d(z)
        trendline = [trendline_func(tick) for tick in steady_ticks]

        plt.figure("Market Price", figsize=(12, 8))
        fig = sns.lineplot(x=ticks, y=prices)
        sns.lineplot(
            x=steady_ticks,
            y=trendline,
            label=f"Trendline - y = {trendline_func.coefficients[0]:0.4f}x + {trendline_func.coefficients[1]:0.4f}",
            color="green",
            legend="brief",
        )

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
        plt.figure("Supply Demand")

        width = 2
        height = int(math.floor(float(len(self.take_snapshots_in)) / float(width)))
        fig, ax = plt.subplots(height, width, figsize=(25, 25))
        fig.suptitle("Supply Demand plots", fontsize=54)

        for i, tick in enumerate(self.take_snapshots_in):
            plot_x = int(i // width)
            plot_y = int(i % width)

            demands = self.history[tick].demands
            supplies = self.history[tick].supplies

            if len(demands) > 0:
                ax[plot_x, plot_y].plot([x[0] for x in demands], [x[1] for x in demands], label="Demand")
            if len(supplies) > 0:
                ax[plot_x, plot_y].plot([x[0] for x in supplies], [x[1] for x in supplies], label="Supply")
            ax[plot_x, plot_y].legend(loc="upper right", fontsize=14)
            ax[plot_x, plot_y].set_title(f"Iteration {tick + 1} - Price = {self.history[tick].price:.2f}", fontsize=24)
            ax[plot_x, plot_y].set_xlabel("Price", fontsize=16)
            ax[plot_x, plot_y].set_ylabel("Quantity", fontsize=16)

        plt.savefig(self.plot_dir + "supply-demand.png")
        plt.close("Supply Demand")
