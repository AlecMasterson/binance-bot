import talib, numpy, math


class Coinpair:

    # Initialize a new Coinpair with the required information
    # Add additional default values for other variables
    def __init__(self, coinpair):
        self.coinpair = coinpair
        self.data = []
        self.macd = []
        self.macdsignal = []
        self.upperband = []
        self.lowerband = []

    # Update the overhead variables associated with the Coinpair
    def update_overhead(self):

        # Use the close price of each Candle to calculate overhead information.
        closeData = [float(candle.close) for candle in self.data]

        # Extremely small numbers (prices) break talib calculations, we must multiply and then divide by 1e6.
        macd, macdsignal, macdhist = talib.MACDFIX(numpy.array(closeData) * 1e6, signalperiod=9)
        upperband, middleband, lowerband = talib.BBANDS(numpy.array(closeData) * 1e6, timeperiod=14, nbdevup=2, nbdevdn=2, matype=0)

        self.macd = macd / 1e6
        self.macdsignal = macdsignal / 1e6
        self.upperband = upperband / 1e6
        self.lowerband = lowerband / 1e6

    # Add a new Candle to the self.data
    # candle - The new Candle being added
    # update - Update the overhead if this is True
    def add_candle(self, candle, update):
        self.data.append(candle)

        # Keep the overhead information up to date.
        if update: self.update_overhead()

    # Add the coinpairs' specific information.
    # info - The specific information, i.e. filters.
    def add_info(self, info):
        self.info = info

    # Determines how many decimal places are used in a float value
    # I.E. 0.0001 returns 4
    # number - The float value
    def num_decimals(self, number):
        count = 0
        while number < 1.0:
            number *= 10
            count += 1
        return count

    # Determine the correct quantity and price of the asset we can purchase
    # Returns -1 and -1 if unable to meet trading requirements
    # balance - How much available BTC we have available
    # price - The price we want to purchase the asset at
    def validate_buy(self, balance, price):

        # Convert the price we want to buy at to the correct format for this coinpair.
        decimalsMinPrice = self.num_decimals(float(self.info['filters'][0]['minPrice']))
        formatPrice = price // float(self.info['filters'][0]['minPrice']) / pow(10, decimalsMinPrice)

        # Convert the amount of BTC we want to use to the correct format for this coinpair.
        # NOTE: Using all available BTC for every buy.
        available = math.floor(balance * pow(10, float(self.info['baseAssetPrecision']))) / pow(10, float(self.info['baseAssetPrecision']))

        # Convert the quantity of our desired asset to the correct format for this coinpair.
        decimalsMinQty = self.num_decimals(float(self.info['filters'][1]['minQty']))
        quantity = (available / formatPrice) // float(self.info['filters'][1]['minQty']) / pow(10, decimalsMinQty)

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
        if valid: return str(quantity), str(formatPrice)
        else: return '-1', '-1'
