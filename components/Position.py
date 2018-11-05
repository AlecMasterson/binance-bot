import sys, os
sys.path.append(os.path.join(os.getcwd(), 'binance-bot'))
import utilities


class Position:
    data = {'OPEN': True, 'COINPAIR': None, 'BTC': None, 'TIME_BUY': None, 'PRICE_BUY': None, 'TIME_SELL': None, 'PRICE_SELL': None, 'ARMED': False, 'ARMED_PRICE': None, 'TOTAL_REWARD': None}

    def __init__(self, coinpair, btc, time_buy, price_buy):
        self.data['COINPAIR'] = coinpair
        self.data['BTC'] = btc
        self.data['TIME_BUY'] = time_buy
        self.data['PRICE_BUY'] = price_buy

    def test_sell(self, time_sell, cur_price):
        result = cur_price / self.data['PRICE_BUY']
        if not self.data['ARMED'] and result > utilities.POSITION_ARM:
            self.data['ARMED'] = True
            self.data['ARMED_PRICE'] = cur_price
        elif not self.data['ARMED'] and result < utilities.POSITION_DROP:
            self.sell(time_sell, cur_price)
            return True
        elif self.data['ARMED']:
            self.data['ARMED_PRICE'] = max(self.data['ARMED_PRICE'], cur_price)
            if cur_price / self.data['ARMED_PRICE'] < utilities.STOP_LOSS:
                self.sell(time_sell, cur_price)
                return True
        return False

    def sell(self, time_sell, price_sell):
        self.data['OPEN'] = False
        self.data['TIME_SELL'] = time_sell
        self.data['PRICE_SELL'] = price_sell
        self.data['TOTAL_REWARD'] = self.data['PRICE_SELL'] / self.data['PRICE_BUY']
