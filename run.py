import math

from miyanmaayeh.runner import Runner


def main():
    for ruuuun in range(1, 16):

        run_time = 500
        steps = math.ceil(run_time / 5)

        config = {
            "snapshots_in": [i for i in range(0, run_time, steps)] + [run_time - 1],
            "plot_dir": f"./plots_2_{ruuuun}/",
            "total_agents": 100,
            "fundamentalist_count": 16.81 / 100,
            "contrarian_count": 5.60 / 100,
            "technical_analyst_count": 23.71 / 100,
            "random_count": 3.88 / 100,
            "long_term_buyer_count": 30.17 / 100,
            "copycat_count": 19.83 / 100,
            "agents-config": {
                "production-average": 1000,
                "production-std": 200,
                "producers-percentage": 20,
                "income-alpha": 4,
                "income-beta": 1500,
            },
        }

        runner = Runner(config=config)
        runner.run(run_time)
        runner.generate_plot()

        prod = sum([item.production for item in runner.agents])
        income = sum([item.income for item in runner.agents])

        print(prod / len(runner.agents), income / len(runner.agents))


if __name__ == "__main__":
    main()
