from binance.client import Client
from components.Candle import Candle
import pandas, os, json, ta, math
import utilities


class Coinpair:

    def __init__(self, client, coinpair):
        self.client = client
        self.coinpair = str(coinpair)
        self.candles = []
        self.overhead = []

        if client != None:
            try:
                data = pandas.DataFrame(self.client.get_klines(symbol=coinpair, interval=utilities.TIME_INTERVAL), columns=utilities.COLUMN_STRUCTURE)
                self.policies = self.client.get_symbol_info(coinpair)
            except:
                utilities.throw_error('Failed to Import Coinpair Historical Data and Info for \'' + coinpair + '\'', True)
        else:
            try:
                data = pandas.read_csv('data/history/' + coinpair + '.csv')
            except:
                utilities.throw_error('data/history/' + coinpair + '.csv FileNotFound', False)
                os.system('python get_history.py -c ' + coinpair)
                data = pandas.read_csv('data/history/' + coinpair + '.csv')

            try:
                with open('data/coinpair/' + coinpair + '.json') as json_file:
                    self.policies = json.load(json_file)
            except:
                utilities.throw_error('Failed to Import Coinpair Historical Data and Info for \'' + coinpair + '\'', True)

        for index, candle in data.iterrows():
            self.candles.append(Candle(candle['Open Time'], candle['Open'], candle['High'], candle['Low'], candle['Close'], candle['Close Time'], candle['Number Trades'], candle['Volume']))

        if not self.update_overhead():
            utilities.throw_error('Failed to Update Coinpair Overhead for \'' + coinpair + '\'', True)

    def update_overhead(self):
        closeData = pandas.Series([candle.close for candle in self.candles])

        macd = ta.trend.macd(closeData, n_fast=12, n_slow=26, fillna=True)
        macdSignal = ta.trend.macd_signal(closeData, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        macdDiff = ta.trend.macd_diff(closeData, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        upperband = ta.volatility.bollinger_hband(closeData, n=14, ndev=2, fillna=True)
        lowerband = ta.volatility.bollinger_lband(closeData, n=14, ndev=2, fillna=True)

        if len(self.candles) != len(macdSignal): return False
        if len(self.candles) != len(macdSignal): return False
        if len(self.candles) != len(macdDiff): return False
        if len(self.candles) != len(upperband): return False
        if len(self.candles) != len(lowerband): return False

        self.overhead = []
        for i in range(0, len(self.candles)):
            self.overhead.append({'macd': macd[i], 'macdSignal': macdSignal[i], 'macdDiff': macdDiff[i], 'upperband': upperband[i], 'lowerband': lowerband[i]})
        return True

    def add_candle(self, candle):
        self.candles.append(candle)
        if not self.update_overhead():
            utilities.throw_error('Failed to Update Coinpair Overhead for \'' + self.coinpair + '\'', True)

    # Determines how many decimal places are used in a float value
    # This is only used to help validate trading precision
    # I.E. 0.0001 returns 4
    def num_decimals(self, number):
        count = 0
        while number < 1.0:
            number *= 10
            count += 1
        return count

    def validate_order(self, type, balance, price):

        # Convert the price we want to order at to the correct format for this coinpair.
        decimalsMinPrice = self.num_decimals(float(self.policies['filters'][0]['minPrice']))
        formatPrice = price // float(self.policies['filters'][0]['minPrice']) / pow(10, decimalsMinPrice)

        # Convert the balance amount provided to use to the correct format for this coinpair.
        # NOTE: Using all available BTC for every buy.
        available = math.floor(balance * pow(10, float(self.policies['baseAssetPrecision']))) / pow(10, float(self.policies['baseAssetPrecision']))

        # The quantity value is determine by price in a buy scenario.
        if type == 'BUY': using = available / formatPrice
        elif type == 'SELL': using = available

        # Convert the quantity of our desired asset to the correct format for this coinpair.
        decimalsMinQty = self.num_decimals(float(self.policies['filters'][1]['minQty']))
        quantity = using // float(self.policies['filters'][1]['minQty']) / pow(10, decimalsMinQty)

        # Test the trading policy filters provided by the symbols dictionary.
        valid = True

        if formatPrice < float(self.policies['filters'][0]['minPrice']): valid = False
        elif formatPrice > float(self.policies['filters'][0]['maxPrice']): valid = False
        elif int((formatPrice - float(self.policies['filters'][0]['minPrice'])) % float(self.policies['filters'][0]['tickSize'])) != 0: valid = False

        if quantity < float(self.policies['filters'][1]['minQty']): valid = False
        elif quantity > float(self.policies['filters'][1]['maxQty']): valid = False
        elif int((quantity - float(self.policies['filters'][1]['minQty'])) % float(self.policies['filters'][1]['stepSize'])) != 0: valid = False

        if quantity * formatPrice < float(self.policies['filters'][2]['minNotional']): valid = False

        # Return the desired trade quantity and price if all is valid.
        # Also return the formatted amount of the balance being used.
        if valid: return quantity, formatPrice
        else: return -1, -1
