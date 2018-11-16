import datetime, pandas, collections, Position


def add_future_potential(old_data, window_size):
    data, window = old_data.copy(), collections.deque(maxlen=window_size)
    for index, row in data.iterrows():
        window.append(row['OPEN'])
        if index >= window_size: data.at[index - window_size, 'FUTURE_POTENTIAL'] = max(window) / data.at[index - window_size, 'OPEN']
    return data


def format_data(data_to_format, start_date, end_date, candle_minutes, future_potential_window_size=None):
    data = data_to_format.copy()
    required_candles = (end_date - start_date).days * 24 * 60 / candle_minutes + 1
    interval_string = '{}h'.format(candle_minutes / 60) if candle_minutes > 30 else '{}m'.format(candle_minutes)

    data = data[(data['INTERVAL'] == interval_string) & (data['OPEN_TIME'] >= start_date.timestamp() * 1000.0)].sort_values(by=['OPEN_TIME']).reset_index(drop=True)
    if not future_potential_window_size is None: data = add_future_potential(data, future_potential_window_size)
    data = data[data['OPEN_TIME'] <= end_date.timestamp() * 1000.0].sort_values(by=['OPEN_TIME']).reset_index(drop=True)
    if len(data) != required_candles: return None
    return data


class Backtest:

    def __init__(self, original_data=None):
        if not original_data is None: self.original_data = original_data.copy()

    def set_data(self, original_data):
        self.original_data = original_data.copy()

    def reset(self, start_date, end_date, starting_balance, candle_minutes, max_positions):
        self.data = self.original_data.copy()

        self.cur_datetime, self.end_datetime = start_date, end_date
        self.candle_minutes, self.max_positions = candle_minutes, max_positions

        self.reward, self.info = {'BALANCE': starting_balance, 'POTENTIAL': 0.0}, {'OPEN_POSITIONS': [], 'FINAL_POSITIONS': []}
        return self.current_state()

    def current_state(self):
        self.epoch = {}
        for key in self.data:
            self.epoch[key] = self.data[key][:1].to_dict(orient='records')[0]
            self.data[key] = self.data[key][1:]

        isDone = False
        if self.cur_datetime == self.end_datetime:
            for position in [position for position in self.info['OPEN_POSITIONS']]:
                self.reward['BALANCE'] += position.data['BTC'] * position.data['TOTAL_REWARD']
                self.info['FINAL_POSITIONS'].append(position)
                self.info['OPEN_POSITIONS'] = [i for i in self.info['OPEN_POSITIONS'] if not position is i]
            isDone = True

        return self.epoch, self.reward, isDone, self.info

    def step(self, action):
        candles = {}
        for key in self.data:
            candles[key] = self.data[key][:1].to_dict(orient='records')[0]

        for position in [position for position in self.info['OPEN_POSITIONS']]:
            if position.test_sell(candles[position.data['COINPAIR']]['OPEN_TIME'], candles[position.data['COINPAIR']]['OPEN']):
                self.reward['BALANCE'] += position.data['BTC'] * position.data['TOTAL_REWARD']
                self.info['FINAL_POSITIONS'].append(position)
                self.info['OPEN_POSITIONS'] = [i for i in self.info['OPEN_POSITIONS'] if not position is i]

        for key in action:
            if not action[key] and 'FUTURE_POTENTIAL' in candles[key]: self.reward['POTENTIAL'] -= candles[key]['FUTURE_POTENTIAL']
            if action[key] and 'FUTURE_POTENTIAL' in candles[key]: self.reward['POTENTIAL'] += candles[key]['FUTURE_POTENTIAL']

            if action[key] and len(self.info['OPEN_POSITIONS']) < self.max_positions and self.reward['BALANCE'] > 0.0:
                new_position = Position.Position(key, self.reward['BALANCE'] / (self.max_positions - len(self.info['OPEN_POSITIONS'])), candles[key]['OPEN_TIME'], candles[key]['OPEN'])
                self.reward['BALANCE'] -= new_position.data['BTC']
                self.info['OPEN_POSITIONS'].append(new_position)

        self.cur_datetime += datetime.timedelta(minutes=self.candle_minutes)
        return self.current_state()
