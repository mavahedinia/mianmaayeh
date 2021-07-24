import matplotlib.pyplot as plt
import numpy as np

from miyanmaayeh.runner import Runner


def main():
    config = {
        "snapshots_in": [0, 1, 2, 3, 4, 5, 25, 50],
        # "snapshots_in": [0, 24, 49, 74, 99],
        "plot_dir": "./plots/",
        "fundamentalist_count": 50,
    }

    run_time = 100

    runner = Runner(config=config)
    runner.run(run_time)
    runner.generate_plot()


if __name__ == "__main__":
    main()
