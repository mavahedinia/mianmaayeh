import math

from miyanmaayeh.market import Market, MarketWithFriction
from miyanmaayeh.runner import Runner


def execute(num):
    run_time = 400
    steps = math.ceil(run_time / 3)

    config = {
        "snapshots_in": [i for i in range(0, run_time, steps)] + [run_time - 1],
        "plot_dir": f"./plots_{num}/",
        "initial_agents": 200,
        "new_agents": 0,
        "average_time_to_add_agents": 0.2,
        # "fundamentalist_count": 16.81 / 100,
        # "contrarian_count": 5.60 / 100,
        # "technical_analyst_count": 23.71 / 100,
        # "random_count": 3.88 / 100,
        # "long_term_buyer_count": 30.17 / 100,
        # "copycat_count": 19.83 / 100,
        "verifier_count": 100 / 100,
        "agents-config": {
            "production-average": 1000,
            "production-std": 200,
            "producers-percentage": 20,
            "income-alpha": 5,
            "income-beta": 6000,
            "initial-inventory": 1000,
            "initial-cash": 5000,
        },
        "market-class": Market,
        "market-options": {
            # "friction_rate": 0.04,
        },
    }

    runner = Runner(config=config)
    runner.run(run_time)
    runner.generate_plot()
    print(sum([item.market_profit for item in runner.history]))


def main():
    execute(3)


if __name__ == "__main__":
    main()
