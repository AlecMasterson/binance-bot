class Wallet:

	def __init__(
		self,
		btc_balance = 0,
		eth_balance = 0
	):
		self.btc_balance = btc_balance
		self.eth_balance = eth_balance

	def buy(self, current_price):
		if (self.btc_balance > 0):
			print "Buying at {} with {} BTC to get {} ETH".format(current_price, self.btc_balance, self.btc_balance * current_price)
			self.eth_balance = self.btc_balance * current_price
			self.btc_balance = 0
	
	def sell(self, current_price):
		if (self.eth_balance > 0):
			print "Selling at {} with {} ETH to get {} BTC".format(current_price, self.eth_balance, self.eth_balance / current_price)
			self.btc_balance = self.eth_balance / current_price
			self.eth_balance = 0