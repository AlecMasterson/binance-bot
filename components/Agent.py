from collections import deque
import sys, os, Backtest
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'scripts'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'components'))
import utilities, helpers, signals


class Agent:

    data = {}
    windows = {}

    def __init__(self, coinpairs):
        for coinpair in coinpairs:
            temp_data = helpers.read_file('data/history/' + coinpair + '.csv')
            temp_data = temp_data[temp_data['INTERVAL'] == utilities.BACKTEST_CANDLE_INTERVAL_STRING]
            temp_data = Backtest.format_data(temp_data)

            if temp_data is None:
                print('Failed to Initialize Coinpair \'{}\'. Continuing Anyway...'.format(coinpair))
                continue
            '''
            print('Calculating Potential...')
            for index, row in temp_data.iterrows():
                if index + 1 + utilities.WINDOW_SIZE >= len(temp_data): continue
                potential = max([row['OPEN'] for index, row in temp_data[index+1:index+1 + utilities.WINDOW_SIZE].iterrows()]) / row['OPEN']
                temp_data.at[index, 'FUTURE_POTENTIAL'] = 1.0 - potential
            '''

            self.data[coinpair] = temp_data
            self.windows[coinpair] = deque(maxlen=utilities.WINDOW_SIZE)

        self.backtest = Backtest.Backtest(self.data)

    def run(self):
        if not self.backtest.reset():
            print('Failed to Initialize Backtest Object')
            return

        state, reward, isDone, info = self.backtest.current_state()
        while not isDone:
            action = self.add_candle(state)
            state, reward, isDone, info = self.backtest.step(action)

        print(reward['BALANCE'])
        #print(info['POTENTIAL_REWARD'])

    def add_candle(self, data):
        action = {}
        for key in [k for k in data if k != 'BALANCE']:
            self.windows[key].append(data[key])
            if len(self.windows[key]) != utilities.WINDOW_SIZE: action[key] = False

            if signals.rsi(self.windows[key]) and signals.volatile(self.windows[key]): action[key] = True
            else: action[key] = False
        return action


if __name__ == '__main__':
    agent = Agent(['ADABTC', 'BNBBTC'])
    agent.run()
