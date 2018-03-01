from binance.client import Client
import re
from candlestick import CandleStick

class Data:

	def getKeys(self):
		file = open("keys.txt", "r")
		for index, line in enumerate(file):
			if index is 0:
				line = re.sub('[\n]', '', line)
				self.api_key = line
			if index is 1:
				self.secret_key = line
		file.close()

	def importData(self):
		self.getKeys()
		client = Client(self.api_key, self.secret_key)
		print("Importing Data... Interval: 1 HOUR - Time Frame: 1 Day")
		klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_1HOUR, "1 day ago UTC")

		file = open("data.txt", "w+")
		for line in klines:
			file.write(str(line))
			file.write('\n')
		file.close()

		print("Complete!")
		return self.readData()

	def readData(self):
		candles = []
		try:
			print("Reading Data...")
			file = open("data.txt", "r")
			for line in file:
				line = re.sub('[\[\'u\n\]]', '', line)
				line_list = line.split(", ")
				temp_candle = CandleStick(
					line_list[0],
					float(line_list[1]),
					float(line_list[2]),
					float(line_list[3]),
					float(line_list[4]),
					float(line_list[5]),
					line_list[6]
				)
				if len(candles) > 0:
					temp_candle.setChange(candles[len(candles)-1])
				candles.append(temp_candle)
			file.close()
		except IOError:
			print("ERROR: Failed to find data.txt")
			return self.importData()
		
		print("Complete!")
		return candles

	def __init__(self):
		self.candles = self.readData()
