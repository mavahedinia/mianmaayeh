import math

from miyanmaayeh.runner import Runner


def main():
    run_time = 500
    steps = math.ceil(run_time / 5)

    config = {
        "snapshots_in": [i for i in range(0, run_time, steps)] + [run_time - 1],
        "plot_dir": "./plots/",
        "fundamentalist_count": 20,
        "contrarian_count": 20,
        "technical_analyst_count": 20,
    }

    runner = Runner(config=config)
    runner.run(run_time)
    runner.generate_plot()


if __name__ == "__main__":
    main()
