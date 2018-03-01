from wallet import Wallet

class BackTest:

	def __init__(self, candles):
		self.candles = candles
		self.person = Wallet(0.08, 0)

	def test(self):
		for index, candle in enumerate(self.candles):
			if index < 3:
				continue
			if self.candles[index-2].change < 0 and self.candles[index-1].change < 0 and candle.change > 0:
				self.person.buy(candle.open_price)
			if self.candles[index-2].change > 0 and self.candles[index-1].change > 0 and candle.change < 0:
				self.person.sell(candle.open_price)

		print("BTC: ", self.person.btc_balance, " ETH: ", self.person.eth_balance)