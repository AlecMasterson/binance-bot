from datetime import datetime
from datetime import timedelta
from collections import deque

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

        cur_datetime = utilities.BACKTEST_START_DATE
        while cur_datetime <= utilities.BACKTEST_END_DATE:

            for position in open_positions:
                for coinpair in data:
                    if coinpair['COINPAIR'] != position.data['COINPAIR']: continue

                    state = coinpair['DATA'][:1].to_dict(orient='records')[0]
                    if position.test_sell(state['OPEN_TIME'], state['OPEN']):
                        self.balance += position.data['BTC'] * position.data['TOTAL_REWARD']
                        open_positions = [x for x in open_positions if not x is position]
                        self.final_positions.append(position)

            for coinpair in data:
                if len(open_positions) >= utilities.MAX_POSITIONS or self.balance <= 0.0: continue
                state = coinpair['DATA'][:1].to_dict(orient='records')[0]

                if state['OPEN_TIME'] == cur_datetime.timestamp():
                    coinpair['DATA'] = coinpair['DATA'][1:]

                    if self.action_function(state):
                        new_position = Position(coinpair['COINPAIR'], self.balance / (utilities.MAX_POSITIONS - len(open_positions)), state['OPEN_TIME'], state['OPEN'])
                        self.balance -= new_position.data['BTC']
                        open_positions.append(new_position)

            cur_datetime += timedelta(minutes=utilities.BACKTEST_CANDLE_INTERVAL)

        return self.balance
