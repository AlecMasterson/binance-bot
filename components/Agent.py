import sys, os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'scripts'))
import utilities, helpers, signals, Backtest
from collections import deque


class Agent:

    data, windows = {}, {}

    def __init__(self):
        self.backtest = Backtest.Backtest()

    def set_data(self, coinpairs):
        self.coinpairs = coinpairs
        for coinpair in self.coinpairs:
            temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
            temp_data = Backtest.format_data(temp_data, utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.BACKTEST_CANDLE_INTERVAL)
            if temp_data is None: return False

            self.data[coinpair] = temp_data
            self.windows[coinpair] = deque(maxlen=utilities.WINDOW_SIZE)

        self.backtest.set_data(self.data)
        return True

    def run(self):
        state, reward, isDone, info = self.backtest.reset(utilities.BACKTEST_START_DATE, utilities.BACKTEST_END_DATE, utilities.STARTING_BALANCE, utilities.BACKTEST_CANDLE_INTERVAL, utilities.MAX_POSITIONS)
        while not isDone:
            action = self.add_candle(state)
            state, reward, isDone, info = self.backtest.step(action)
        print('Final Balance: {}\n'.format(reward['BALANCE']))

    def add_candle(self, state):
        action = {}
        for key in state:
            self.windows[key].append(state[key])
            if len(self.windows[key]) != utilities.WINDOW_SIZE: action[key] = False
            elif signals.rsi(self.windows[key]): action[key] = True
            else: action[key] = False
        return action


if __name__ == '__main__':
    agent = Agent()
    if agent.set_data(['ADABTC', 'BNBBTC']): agent.run()
