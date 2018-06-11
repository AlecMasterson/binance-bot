class Candle:

    # Initialize a new Candle with the required information
    def __init__(self, openTime, open, high, low, close, closeTime, numTrades, volume):
        self.openTime = openTime
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.closeTime = closeTime
        self.numTrades = numTrades
        self.volume = volume
