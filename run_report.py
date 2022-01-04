import math
from pathlib import Path

import dill
import matplotlib.pyplot as plt
import seaborn as sns

from miyanmaayeh.market import Market, MarketWithFriction
from miyanmaayeh.runner import Runner

RUNS = 3
FRICTION_STEPS = 0.02

PLOT_DIR = "reports/"
Path(PLOT_DIR).mkdir(parents=True, exist_ok=True)


results = {}


def execute(num, friction_rate):
    run_time = 400
    steps = math.ceil(run_time / 5)

    config = {
        "snapshots_in": [i for i in range(0, run_time, steps)] + [run_time - 1],
        "plot_dir": f"./reports/plots_{friction_rate:.3f}_{num}/",
        "initial_agents": 25,
        "new_agents": 100,
        "average_time_to_add_agents": 0.5,
        "fundamentalist_count": 16.81 / 100,
        "contrarian_count": 5.60 / 100,
        "technical_analyst_count": 23.71 / 100,
        "random_count": 3.88 / 100,
        "long_term_buyer_count": 30.17 / 100,
        "copycat_count": 19.83 / 100,
        # "verifier_count": 100 / 100,
        "agents-config": {
            "production-average": 3000,
            "production-std": 200,
            "producers-percentage": 20,
            "income-alpha": 10,
            "income-beta": 1500,
            "initial-inventory": 1000,
            "initial-cash": 1000,
        },
        "market-class": MarketWithFriction,
        "market-options": {
            "friction_rate": friction_rate,
        },
    }

    runner = Runner(config=config)
    runner.run(run_time)

    persist_f_name = config["plot_dir"] + "runner.dill"
    with open(persist_f_name, "wb") as f:
        dill.dump(runner, f)

    runner.generate_plot()

    result = sum([item.market_profit for item in runner.history])
    if friction_rate not in results:
        results[friction_rate] = []

    results[friction_rate].append(result)


def generate_plot(points):
    sns.set_theme()

    plt.figure("Mu - Profit", figsize=(12, 8))
    fig = sns.lineplot(x=[x[0] for x in points], y=[x[1] for x in points])

    fig.set(xlabel="Mu", ylabel="Profit", title="Market Price")

    plt.savefig(PLOT_DIR + "mu-profit.png")
    plt.close("Mu - Profit")


def main():
    frs = [fr * FRICTION_STEPS for fr in range(int(1 / FRICTION_STEPS))]

    for fr in frs:
        for r in range(RUNS):
            execute(r, fr)

    points = []

    for fr in frs:
        avg = sum(results[fr]) / len(results[fr])
        points.append((fr, avg))

    generate_plot(points)


if __name__ == "__main__":
    main()
