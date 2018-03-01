from wallet import Wallet

class BackTest:

	def __init__(self, candles):
		self.candles = candles
		self.person = Wallet(0.08, 0)

	def buy(self, candle):
		if (self.person.btc_balance > 0):
			print "Buying at {} with {} BTC to get {} ETH".format(candle.open_price, self.person.btc_balance, self.person.btc_balance * candle.open_price)
			self.person.eth_balance = self.person.btc_balance * candle.open_price
			self.person.btc_balance = 0

	def sell(self, candle):
		if (self.person.eth_balance > 0):
			print "Selling at {} with {} ETH to get {} BTC".format(candle.open_price, self.person.eth_balance, self.person.eth_balance / candle.open_price)
			self.person.btc_balance = self.person.eth_balance / candle.open_price
			self.person.eth_balance = 0

	def test(self):
		for index, candle in enumerate(self.candles):
			if index < 3:
				continue
			if self.candles[index-2].change < 0 and self.candles[index-1].change < 0 and candle.change > 0:
				self.buy(candle)
			if self.candles[index-2].change > 0 and self.candles[index-1].change > 0 and candle.change < 0:
				self.sell(candle)

		print("BTC: ", self.person.btc_balance, " ETH: ", self.person.eth_balance)