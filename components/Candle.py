class Candle:

    def __init__(self, openTime, open, high, low, close, closeTime, numTrades, volume):
        self.openTime = int(openTime)
        self.open = float(open)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.closeTime = int(closeTime)
        self.numTrades = int(numTrades)
        self.volume = int(volume)
