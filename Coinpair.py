import talib, numpy


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