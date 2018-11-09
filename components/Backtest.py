from datetime import datetime
from datetime import timedelta
import sys, os
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'components'))
import utilities
from Position import Position


class Backtest:

    final_positions = []
    balance = utilities.STARTING_BALANCE

    def __init__(self, action_function):
        self.action_function = action_function

    def reset(self):
        self.final_positions = []
        self.balance = utilities.STARTING_BALANCE

    def backtest(self, data):
        open_positions = []

        for key, coinpair in data.items():
            data[key] = data[key][data[key]['OPEN_TIME'] >= utilities.BACKTEST_START_DATE.timestamp() * 1000.0]

        cur_datetime = utilities.BACKTEST_START_DATE
        while cur_datetime <= utilities.BACKTEST_END_DATE:

            for position in open_positions:
                for key, coinpair in data.items():
                    if key != position.data['COINPAIR']: continue

                    candle = data[key][:1].to_dict(orient='records')[0]
                    if position.test_sell(candle['OPEN_TIME'], candle['OPEN']):
                        self.balance += position.data['BTC'] * position.data['TOTAL_REWARD']
                        open_positions = [x for x in open_positions if not x is position]
                        self.final_positions.append(position)
                    break

            epoch = {}
            for key, coinpair in data.items():
                if len(open_positions) >= utilities.MAX_POSITIONS or self.balance <= 0.0: continue
                candle = data[key][:1].to_dict(orient='records')[0]

                if candle['OPEN_TIME'] == cur_datetime.timestamp() * 1000.0:
                    data[key] = data[key][1:]

                epoch[key] = candle

            actions = self.action_function(epoch)
            for a in [actions[k] for k in actions if actions[k] == True]:
                new_position = Position(key, self.balance / (utilities.MAX_POSITIONS - len(open_positions)), candle['OPEN_TIME'], candle['OPEN'])
                self.balance -= new_position.data['BTC']
                open_positions.append(new_position)

            cur_datetime += timedelta(minutes=utilities.BACKTEST_CANDLE_INTERVAL)

        for position in open_positions:
            self.balance += position.data['BTC'] * position.data['TOTAL_REWARD']

        return self.balance
