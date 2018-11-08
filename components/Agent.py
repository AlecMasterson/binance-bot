from collections import deque
import sys, os
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'scripts'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'components'))
import utilities, helpers, signals
from Backtest import Backtest


class Agent:

    data = {}
    windows = {}

    def __init__(self, coinpairs):
        for coinpair in coinpairs:
            temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
            if temp_data is None: return 1

            self.data[coinpair] = temp_data[temp_data['INTERVAL'] == utilities.BACKTEST_CANDLE_INTERVAL_STRING].sort_values(by=['OPEN_TIME']).reset_index(drop=True)
            self.windows[coinpair] = deque(maxlen=utilities.WINDOW_SIZE)

        self.backtest = Backtest(self.add_candle)

    def run(self):
        print(self.backtest.backtest(self.data))

    def add_candle(self, data):
        self.windows[data['COINPAIR']].append(data['CANDLE'])

        if signals.rsi(self.windows[data['COINPAIR']]) and signals.lowerband(self.windows[data['COINPAIR']]): return True

        return False


if __name__ == '__main__':
    agent = Agent(['ADABTC', 'BNBBTC'])
    agent.run()
