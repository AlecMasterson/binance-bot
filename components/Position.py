import sys, os
sys.path.append(os.getcwd())
import utilities


class Position:

    def __init__(self, coinpair, btc, time_buy, price_buy):
        self.data = {'OPEN': True, 'COINPAIR': coinpair, 'BTC': btc, 'TIME_BUY': time_buy, 'PRICE_BUY': price_buy, 'TIME_SELL': None, 'PRICE_SELL': None, 'HIGH': price_buy, 'TOTAL_REWARD': 1.0}

    def test_sell(self, time_sell, price_sell):
        self.data['HIGH'] = max(self.data['HIGH'], price_sell)
        self.data['TOTAL_REWARD'] = price_sell / self.data['PRICE_BUY']

        if self.data['TOTAL_REWARD'] < utilities.POSITION_DROP or (self.data['HIGH'] / self.data['PRICE_BUY'] > utilities.MIN_GAIN and price_sell / self.data['HIGH'] < utilities.STOP_LOSS):
            self.sell(time_sell, price_sell)
            return True
        return False

    def sell(self, time_sell, price_sell):
        self.data['OPEN'] = False
        self.data['TIME_SELL'] = time_sell
        self.data['PRICE_SELL'] = price_sell
