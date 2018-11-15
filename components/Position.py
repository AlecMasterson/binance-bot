import sys, os
sys.path.append(os.getcwd())
import utilities


class Position:
    data = {'OPEN': True, 'COINPAIR': None, 'BTC': None, 'TIME_BUY': None, 'PRICE_BUY': None, 'TIME_SELL': None, 'PRICE_SELL': None, 'HIGH': None, 'TOTAL_REWARD': None}

    def __init__(self, coinpair, btc, time_buy, price_buy):
        self.data['COINPAIR'] = coinpair
        self.data['BTC'] = btc
        self.data['TIME_BUY'] = time_buy
        self.data['PRICE_BUY'] = price_buy

    def test_sell(self, time_sell, price_sell):
        result = price_sell / self.data['PRICE_BUY']
        self.data['HIGH'] = price_sell if self.data['HIGH'] is None else max(self.data['HIGH'], price_sell)
        self.data['TOTAL_REWARD'] = result

        if result < utilities.POSITION_DROP or price_sell / self.data['HIGH'] < utilities.STOP_LOSS:
            self.sell(time_sell, price_sell)
            return True
        return False

    def sell(self, time_sell, price_sell):
        self.data['OPEN'] = False
        self.data['TIME_SELL'] = time_sell
        self.data['PRICE_SELL'] = price_sell
        self.data['TOTAL_REWARD'] = self.data['PRICE_SELL'] / self.data['PRICE_BUY']
