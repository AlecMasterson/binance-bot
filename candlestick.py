class CandleStick:

	def __init__(
		self,
		open_time = -1,
		open_price = -1,
		high = -1,
		low = -1,
		close_price = -1,
		volume = -1,
		close_time = -1
	):
		self.open_time = open_time
		self.open_price = open_price
		self.high = high
		self.low = low
		self.close_price = close_price
		self.volume = volume
		self.close_time = close_time

	def setChange(self, other_candle):
		self.change = (self.close_price / other_candle.close_price) - 1