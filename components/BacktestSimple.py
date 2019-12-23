class BacktestSimple:

    def __init__(self, original_data, start_datetime, end_datetime, time_change):
        self.original_data, self.start_datetime, self.end_datetime, self.time_change = original_data.copy(), start_datetime, end_datetime, time_change

    def reset(self):
        self.data, self.cur_datetime = self.original_data.copy(), self.start_datetime
        self.epoch, self.reward, self.info = self.new_candle(), 0.0, {}
        return self.current_state()

    def current_state(self):
        return self.epoch, self.reward, self.cur_datetime == self.end_datetime, self.info

    def step(self, action):
        self.new_candle()

        self.reward = self.epoch['FUTURE_POTENTIAL']
        self.epoch.pop('FUTURE_POTENTIAL')

        self.cur_datetime += self.time_change
        return self.current_state()

    def new_candle(self):
        self.epoch = self.data[:1].to_dict(orient='records')[0]
        self.data = self.data[1:]
