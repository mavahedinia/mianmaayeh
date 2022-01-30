import math
from copy import deepcopy
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from miyanmaayeh.runner import Runner
from miyanmaayeh.utils import get_steady_state

PLOT_DIR = "verification/"
Path(PLOT_DIR).mkdir(parents=True, exist_ok=True)

NUM_RUNS = 5
ITERS = 500


def generate_plots(runners):
    sns.set_theme()
    plt.figure("Verification")

    width = NUM_RUNS
    height = int(math.floor(float(len(runners)) / float(width)))
    fig, ax = plt.subplots(height, width, figsize=(45, 25))
    fig.suptitle("Market Prices", fontsize=54)

    for i, item in enumerate(runners):
        config, runner = item[0], item[1]

        plot_x = int(i // width)
        plot_y = int(i % width)

        prices = [item.price for item in runner.history]
        ticks = np.arange(0, len(prices))

        steady_ticks, steady_prices = get_steady_state(prices)

        z = np.polyfit(steady_ticks, steady_prices, 1)
        trendline_func = np.poly1d(z)
        trendline = [trendline_func(tick) for tick in steady_ticks]

        ax[plot_x, plot_y].plot(ticks, prices, label="Market Price")
        ax[plot_x, plot_y].plot(
            steady_ticks,
            trendline,
            label=f"Trendline - y = {trendline_func.coefficients[0]:0.4f}x + {trendline_func.coefficients[1]:0.4f}",
            color="green",
        )
        ax[plot_x, plot_y].legend(loc="upper right", fontsize=14)
        ax[plot_x, plot_y].set_title(
            f"Cash={config['agents-config']['initial-cash']}, INV={config['agents-config']['initial-inventory']} - {i % NUM_RUNS + 1}",
            fontsize=24,
        )
        ax[plot_x, plot_y].set_xlabel("Time", fontsize=16)
        ax[plot_x, plot_y].set_ylabel("Price", fontsize=16)

    plt.savefig(PLOT_DIR + "prices.png")
    plt.close("Verification")


def main():
    steps = math.ceil(ITERS / 1)

    config = {
        "snapshots_in": [i for i in range(0, ITERS, steps)] + [ITERS - 1],
        "initial_agents": 300,
        "verifier_count": 100 / 100,
        "agents-config": {
            "production-average": 3000,
            "production-std": 200,
            "producers-percentage": 0,
            "income-alpha": 4,
            "income-beta": 0,
            "initial-inventory": 1000,
            "initial-cash": 20000,
        },
    }

    runners = []

    for i in range(NUM_RUNS):
        runner = Runner(config=config)
        runner.run(ITERS)
        runners.append((deepcopy(config), runner))

    config["agents-config"]["initial-cash"] *= 2

    for i in range(NUM_RUNS):
        runner = Runner(config=config.copy())
        runner.run(ITERS)
        runners.append((deepcopy(config), runner))

    config["agents-config"]["initial-cash"] /= 2
    config["agents-config"]["initial-inventory"] *= 2

    for i in range(NUM_RUNS):
        runner = Runner(config=config.copy())
        runner.run(ITERS)
        runners.append((deepcopy(config), runner))

    generate_plots(runners)


if __name__ == "__main__":
    main()
