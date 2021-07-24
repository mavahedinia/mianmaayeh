from miyanmaayeh.runner import Runner


def main():
    config = {
        "snapshots_in": [i for i in range(0, 200, 25)],
        "plot_dir": "./plots/",
        "fundamentalist_count": 50,
    }

    run_time = 200

    runner = Runner(config=config)
    runner.run(run_time)
    runner.generate_plot()


if __name__ == "__main__":
    main()
