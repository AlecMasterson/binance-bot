from binance.client import Client
from components.Candle import Candle
import pandas, os, json, ta, math
import utilities


class Coinpair:

    def __init__(self, client, coinpair):
        self.client = client
        self.coinpair = coinpair
        self.candles = pandas.DataFrame(columns=['time', 'candle'])
        self.overhead = pandas.DataFrame(columns=['time', 'macd', 'macdSignal', 'macdDiff', 'upperband', 'lowerband'])

        if client != None:
            data = pandas.DataFrame(self.client.get_klines(symbol=coinpair, interval=utilities.TIME_INTERVAL), columns=utilities.COLUMN_STRUCTURE)
            self.info = self.client.get_symbol_info(coinpair)
        else:
            try:
                data = pandas.read_csv('data/history/' + coinpair + '.csv')
            except:
                utilities.throw_info('data/history/' + coinpair + '.csv FileNotFound')
                os.system('python get_history_new.py -c ' + coinpair)
                data = pandas.read_csv('data/history/' + coinpair + '.csv')

            try:
                with open('data/coinpair/' + coinpair + '.json') as json_file:
                    self.info = json.load(json_file)
            except:
                utilities.throw_error('Failed to Import Coinpair History or Info', True)

        for index, candle in data.iterrows():
            newCandle = Candle(
                int(candle['Open Time']), float(candle['Open']), float(candle['High']), float(candle['Low']), float(candle['Close']), int(candle['Close Time']), int(candle['Number Trades']),
                float(candle['Volume']))
            self.candles = self.candles.append({'time': newCandle.openTime, 'candle': newCandle}, ignore_index=True)

        self.candles = self.candles.set_index('time')
        self.update_overhead()
        self.overhead = self.overhead.set_index('time')

    def update_overhead(self):
        closeData = pandas.Series([row['candle'].close for index, row in self.candles.iterrows()])

        macd = ta.trend.macd(closeData, n_fast=12, n_slow=26, fillna=True)
        macdSignal = ta.trend.macd_signal(closeData, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        macdDiff = ta.trend.macd_diff(closeData, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        upperband = ta.volatility.bollinger_hband(closeData, n=14, ndev=2, fillna=True)
        lowerband = ta.volatility.bollinger_lband(closeData, n=14, ndev=2, fillna=True)

        i = 0
        for index, row in self.candles.iterrows():
            self.overhead = self.overhead.append(
                {
                    'time': index,
                    'macd': macd[i],
                    'macdSignal': macdSignal[i],
                    'macdDiff': macdDiff[i],
                    'upperband': upperband[i],
                    'lowerband': lowerband[i]
                }, ignore_index=True)
            i += 1

    def add_candle(self, candle):
        self.candles = self.candles.append({'time': candle.openTime, 'candle': candle})
        self.update_overhead()

    # Determines how many decimal places are used in a float value
    # This is only used to help validate trading precision
    # I.E. 0.0001 returns 4
    # number - The float value
    def num_decimals(self, number):
        count = 0
        while number < 1.0:
            number *= 10
            count += 1
        return count

    # Determine the correct quantity and price we can buy/sell
    # Returns -1, -1, and -1 if unable to meet trading requirements
    # type - Whether it's a buy or sell order
    # balance - How much of the asset being used to buy/sell we have available
    # price - The price we want to buy/sell the asset at
    def validate_order(self, type, balance, price):

        # Convert the price we want to order at to the correct format for this coinpair.
        decimalsMinPrice = self.num_decimals(float(self.info['filters'][0]['minPrice']))
        formatPrice = price // float(self.info['filters'][0]['minPrice']) / pow(10, decimalsMinPrice)

        # Convert the balance amount provided to use to the correct format for this coinpair.
        # NOTE: Using all available BTC for every buy.
        available = math.floor(balance * pow(10, float(self.info['baseAssetPrecision']))) / pow(10, float(self.info['baseAssetPrecision']))

        # The quantity value is determine by price in a buy scenario.
        if type == 'BUY': using = available / formatPrice
        elif type == 'SELL': using = available

        # Convert the quantity of our desired asset to the correct format for this coinpair.
        decimalsMinQty = self.num_decimals(float(self.info['filters'][1]['minQty']))
        quantity = using // float(self.info['filters'][1]['minQty']) / pow(10, decimalsMinQty)

        # Test the trading policy filters provided by the symbols dictionary.
        valid = True

        if formatPrice < float(self.info['filters'][0]['minPrice']): valid = False
        elif formatPrice > float(self.info['filters'][0]['maxPrice']): valid = False
        elif int((formatPrice - float(self.info['filters'][0]['minPrice'])) % float(self.info['filters'][0]['tickSize'])) != 0: valid = False

        if quantity < float(self.info['filters'][1]['minQty']): valid = False
        elif quantity > float(self.info['filters'][1]['maxQty']): valid = False
        elif int((quantity - float(self.info['filters'][1]['minQty'])) % float(self.info['filters'][1]['stepSize'])) != 0: valid = False

        if quantity * formatPrice < float(self.info['filters'][2]['minNotional']): valid = False

        # Return the desired trade quantity and price if all is valid.
        # Also return the formatted amount of the balance being used.
        if valid: return quantity, formatPrice, available
        else: return -1, -1, -1
