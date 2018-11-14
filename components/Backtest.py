import sys, os, datetime, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'components'))
import utilities
from Position import Position


def format_data(self, format_data):
    data = format_data.copy()
    required_candles = (utilities.BACKTEST_END_DATE - utilities.BACKTEST_START_DATE).days * 24 * 60 / utilities.BACKTEST_CANDLE_INTERVAL + 1

    data = data[data['OPEN_TIME'] >= utilities.BACKTEST_START_DATE.timestamp() * 1000.0]
    data = data[data['OPEN_TIME'] <= utilities.BACKTEST_END_DATE.timestamp() * 1000.0]
    data = data.sort_values(by=['OPEN_TIME']).reset_index(drop=True)
    if len(self.data[key]) != required_candles: return None

    return data


class Backtest:

    def __init__(self, original_data):
        self.original_data = original_data.copy()

    def reset(self):
        self.data = self.original_data.copy()
        if not self.set_data(): return False

        self.final_positions, self.open_positions = [], []
        self.reward, self.info = {'BALANCE': utilities.STARTING_BALANCE}, {}
        self.cur_datetime = utilities.BACKTEST_START_DATE
        return True

    def current_state(self):
        self.epoch = {}
        for key in self.data:
            self.epoch[key] = self.data[key][:1].to_dict(orient='records')[0]
            self.data[key] = self.data[key][1:]

        isDone = False
        if self.cur_datetime == utilities.BACKTEST_END_DATE:
            for position in self.open_positions:
                self.reward['BALANCE'] += position.data['BTC'] * position.data['TOTAL_REWARD']
            isDone = True

        return self.epoch, self.reward, isDone, self.info

    def step(self, action):
        for position in self.open_positions:
            candle = self.data[position.data['COINPAIR']][:1].to_dict(orient='records')[0]
            if position.test_sell(candle['OPEN_TIME'], candle['OPEN']):
                self.reward['BALANCE'] += position.data['BTC'] * position.data['TOTAL_REWARD']
                self.open_positions = [x for x in self.open_positions if not x is position]
                self.final_positions.append(position)

        for key in [k for k in action if action[k] == True]:
            if len(self.open_positions) >= utilities.MAX_POSITIONS or self.reward['BALANCE'] <= 0.0: continue

            candle = self.data[key][:1].to_dict(orient='records')[0]
            new_position = Position(key, self.reward['BALANCE'] / (utilities.MAX_POSITIONS - len(self.open_positions)), candle['OPEN_TIME'], candle['OPEN'])
            self.reward['BALANCE'] -= new_position.data['BTC']
            self.open_positions.append(new_position)

        self.cur_datetime += datetime.timedelta(minutes=utilities.BACKTEST_CANDLE_INTERVAL)
        return self.current_state()
