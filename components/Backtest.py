from datetime import datetime
from datetime import timedelta
import sys, os, pandas
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
sys.path.append(os.path.join(os.getcwd(), 'binance-bot', 'components'))
import utilities
from Position import Position


class Backtest:

    final_positions = []
    balance = utilities.STARTING_BALANCE

    def __init__(self, action_function, original_data):
        self.action_function = action_function
        self.original_data = original_data
        self.data = original_data.copy()

    def reset(self):
        self.final_positions = []
        self.balance = utilities.STARTING_BALANCE
        self.data = self.original_data.copy()

    def backtest(self):
        open_positions = []

        # Remove all candles before the starting timestep.
        for key in self.data:
            self.data[key] = self.data[key][self.data[key]['OPEN_TIME'] >= utilities.BACKTEST_START_DATE.timestamp() * 1000.0]
            self.data[key] = self.data[key].sort_values(by=['OPEN_TIME']).reset_index(drop=True)

        cur_datetime = utilities.BACKTEST_START_DATE
        while cur_datetime <= utilities.BACKTEST_END_DATE:

            # Attempt to sell any open position.
            for position in open_positions:
                for key in [k for k in self.data if k == position.data['COINPAIR']]:
                    candle = self.data[key][:1].to_dict(orient='records')[0]
                    if position.test_sell(candle['OPEN_TIME'], candle['OPEN']):
                        self.balance += position.data['BTC'] * position.data['TOTAL_REWARD']
                        open_positions = [x for x in open_positions if not x is position]
                        self.final_positions.append(position)

            # Get the current state of the backtesting.
            epoch = {'BALANCE': self.balance}
            for key in self.data:
                epoch[key] = self.data[key][:1].to_dict(orient='records')[0]
                self.data[key] = self.data[key][1:]

            # Attempt to buy any coinpair.
            actions = self.action_function(epoch)
            for key in [k for k in actions if actions[k] == True]:
                if len(open_positions) >= utilities.MAX_POSITIONS or self.balance <= 0.0: continue

                new_position = Position(key, self.balance / (utilities.MAX_POSITIONS - len(open_positions)), epoch[key]['OPEN_TIME'], epoch[key]['OPEN'])
                self.balance -= new_position.data['BTC']
                open_positions.append(new_position)

            cur_datetime += timedelta(minutes=utilities.BACKTEST_CANDLE_INTERVAL)

        # Close any open position.
        for position in open_positions:
            self.balance += position.data['BTC'] * position.data['TOTAL_REWARD']

        return self.balance
