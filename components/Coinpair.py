from binance.client import Client
from components.Candle import Candle
import pandas, ta, math, json
import utilities


class Coinpair:

    # Initialize a new Coinpair with the required information
    # Add additional default values for other variables
    # NOTE: This has 2 API calls
    def __init__(self, client, coinpair, online):
        self.client = client
        self.coinpair = coinpair
        self.candles = []
        self.macd = []
        self.macdSignal = []
        self.macdDiff = []
        self.upperband = []
        self.lowerband = []

        # Query the API for the latest 500 entry points and the coinpair's specific info.
        if online:
            tempData = pandas.DataFrame(self.client.get_klines(symbol=self.coinpair, interval=Client.KLINE_INTERVAL_5MINUTE), columns=utilities.COLUMN_STRUCTURE)
            self.info = self.client.get_symbol_info(self.coinpair)
        else:
            try:
                tempData = pandas.read_csv('data/history/' + coinpair + '.csv')
                saveToFile = False
            except FileNotFoundError:
                if client == None: raise Exception('No Client')
                utilities.throw_info('data/history/' + coinpair + '.csv FileNotFound... using API...')
                tempData = pandas.DataFrame(
                    self.client.get_historical_klines(symbol=self.coinpair, interval=Client.KLINE_INTERVAL_5MINUTE, start_str='1527724800000', end_str='1528070400000'),
                    columns=utilities.COLUMN_STRUCTURE)
                saveToFile = True
            except:
                utilities.throw_error('Failed to Retrieve Historical Data', True)

            try:
                if saveToFile: tempData.to_csv('data/history/' + coinpair + '.csv', index=False)
            except:
                utilities.throw_error('Failed to Save Historical Data', False)

            # Add the specific information associated with this Coinpair.
            # This is used below to verify trading precision.
            try:
                with open('data/coinpair/' + coinpair + '.json') as json_file:
                    self.info = json.load(json_file)
                saveToFile = False
            except FileNotFoundError:
                if client == None: raise Exception('No Client')
                utilities.throw_info('data/coinpair/' + coinpair + '.json FileNotFound... using API...')
                self.info = self.client.get_symbol_info(self.coinpair)
                saveToFile = True
            except:
                utilities.throw_error('Failed to Coinpair Info', True)

            try:
                if saveToFile:
                    with open('data/coinpair/' + coinpair + '.json', 'w') as json_file:
                        json.dump(self.info, json_file)
            except:
                utilities.throw_error('Failed to Save Coinpair Info', False)

        # Create a Candle and add it to self.candles for each entry returned by the API.
        # Remove the last one as that's the current (incomplete) Candle.
        for index, candle in tempData.iterrows():
            self.candles.append(Candle(int(candle['Open Time']), float(candle['Open']), float(candle['High']), float(candle['Low']), float(candle['Close']), int(candle['Close Time'])))
        self.candles = self.candles[:-1]

        # Update the overhead information for this Coinpair.
        # Overhead information includes the MACD, Bollinger Bands, etc.
        self.update_overhead()

    # Update the overhead variables associated with the Coinpair
    def update_overhead(self):

        # Use the close price of each Candle to calculate overhead information.
        closeData = pandas.Series([float(candle.close) for candle in self.candles])

        # Use the ta library to calculate the following pieces of overhead information.
        self.macd = ta.trend.macd(closeData, n_fast=12, n_slow=26, fillna=True)
        self.macdSignal = ta.trend.macd_signal(closeData, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        self.macdDiff = ta.trend.macd_diff(closeData, n_fast=12, n_slow=26, n_sign=9, fillna=True)
        self.upperband = ta.volatility.bollinger_hband(closeData, n=14, ndev=2, fillna=True)
        self.lowerband = ta.volatility.bollinger_lband(closeData, n=14, ndev=2, fillna=True)

    # Add a new Candle to the self.candles array and keep the overhead information updated
    # candle - The new Candle being added
    def add_candle(self, candle):
        self.candles.append(candle)
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
