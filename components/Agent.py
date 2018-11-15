import sys, os, collections, pandas
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import utilities, helpers, signals, Backtest


class Agent:

    data, windows = {}, {}

    def __init__(self, export=False):
        self.export = export
        self.backtest = Backtest.Backtest()

    def set_data(self, coinpairs):
        self.coinpairs = coinpairs
        for coinpair in self.coinpairs:
            temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
            temp_data = Backtest.format_data(temp_data, utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.BACKTEST_CANDLE_INTERVAL, 24)
            if temp_data is None: return False

            self.data[coinpair] = temp_data
            self.windows[coinpair] = collections.deque(maxlen=utilities.WINDOW_SIZE)

        self.backtest.set_data(self.data)
        return True

    def run(self):
        state, reward, isDone, info = self.backtest.reset(utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.STARTING_BALANCE, utilities.BACKTEST_CANDLE_INTERVAL, utilities.MAX_POSITIONS)
        while not isDone:
            action = self.add_candle(state)
            state, reward, isDone, info = self.backtest.step(action)
        print('Final Balance: {}\nPotential Reward: {}\n'.format(reward['BALANCE'], reward['POTENTIAL']))

        if self.export:
            final_positions = pandas.DataFrame(columns=['OPEN', 'COINPAIR', 'BTC', 'TIME_BUY', 'PRICE_BUY', 'TIME_SELL', 'PRICE_SELL', 'HIGH', 'TOTAL_REWARD'])
            for position in self.backtest.final_positions:
                final_positions = final_positions.append(position.data, ignore_index=True)
            final_positions.to_csv('data/plots/backtest_results.csv')

    def add_candle(self, state):
        action = {}
        for key in state:
            self.windows[key].append(state[key])
            if len(self.windows[key]) != utilities.WINDOW_SIZE: action[key] = False
            elif signals.rsi(self.windows[key]): action[key] = True
            else: action[key] = False
        return action


if __name__ == '__main__':
    agent = Agent(export=True)
    if agent.set_data(['ADABTC', 'BNBBTC']): agent.run()
