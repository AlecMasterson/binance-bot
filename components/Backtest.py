import sys, os, datetime, pandas
sys.path.append(os.getcwd())
import Position


def format_data(data_to_format, start_date, end_date, candle_minutes):
    data = data_to_format.copy()
    required_candles = (end_date - start_date).days * 24 * 60 / candle_minutes + 1
    interval_string = '{}h'.format(candle_minutes / 60) if candle_minutes > 30 else '{}m'.format(candle_minutes)

    data = data[(data['INTERVAL'] == interval_string) & (data['OPEN_TIME'] >= start_date.timestamp() * 1000.0) & (data['OPEN_TIME'] <= end_date.timestamp() * 1000.0)].sort_values(by=['OPEN_TIME']).reset_index(drop=True)
    if len(data) != required_candles: return None
    return data


class Backtest:

    def __init__(self, original_data):
        self.original_data = original_data.copy()

    def set_data(self, original_data):
        self.original_data = original_data.copy()

    def reset(self, start_date, end_date, starting_balance, candle_minutes, max_positions):
        self.data = self.original_data.copy()

        self.cur_datetime, self.end_datetime = start_date, end_date
        self.final_positions, self.all_positions = [], []
        self.candle_minutes, self.max_positions = candle_minutes, max_positions

        self.reward, self.info = {'BALANCE': starting_balance}, {}
        return self.current_state()

    def current_state(self):
        self.epoch = {}
        for key in self.data:
            self.epoch[key] = self.data[key][:1].to_dict(orient='records')[0]
            self.data[key] = self.data[key][1:]

        isDone = False
        if self.cur_datetime == self.end_datetime:
            for position in self.all_positions:
                self.reward['BALANCE'] += position.data['BTC'] * position.data['TOTAL_REWARD']
            isDone = True

        return self.epoch, self.reward, isDone, self.info

    def step(self, action):
        for position in [all_position for all_position in self.all_positions if all_position.data['OPEN']]:
            candle = self.data[position.data['COINPAIR']][:1].to_dict(orient='records')[0]
            if position.test_sell(candle['OPEN_TIME'], candle['OPEN']):
                self.reward['BALANCE'] += position.data['BTC'] * position.data['TOTAL_REWARD']
                self.final_positions.append(position)

        for key in [k for k in action if action[k] == True]:
            if len(self.all_positions) >= self.max_positions or self.reward['BALANCE'] <= 0.0: continue

            candle = self.data[key][:1].to_dict(orient='records')[0]
            new_position = Position.Position(key, self.reward['BALANCE'] / (self.max_positions - len(self.all_positions)), candle['OPEN_TIME'], candle['OPEN'])
            self.reward['BALANCE'] -= new_position.data['BTC']
            self.all_positions.append(new_position)

        self.cur_datetime += datetime.timedelta(minutes=self.candle_minutes)
        return self.current_state()
