from bayes_opt import BayesianOptimization
from Bot import Bot
import utilities

if __name__ == "__main__":
    bot = Bot(False, True)
    import Bot

    bo = BayesianOptimization(lambda test: Bot.run_backtest(bot, utilities.COINPAIRS[0]), {'test': (3.0, 3.0)})
    bo.maximize(init_points=50, n_iter=1, kappa=2)

    print(bo.res['max'])
