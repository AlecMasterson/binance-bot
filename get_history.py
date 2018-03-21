from binance.client import Client
import pandas, sys, time

try:
	client = Client("", "")
except:
	print("ERROR: Could Not Connect to API Client!")
	sys.exit()

def create_frame(data):
	return pandas.DataFrame(
		data,
		columns=[
			"Open Time", "Open", "High", "Low",
			"Close", "Volume", "Close Time", "Quote Asset Volume",
			"Number Trades", "Taker Base Asset Volume", "Take Quote Asset Volume", "Ignore"
		]
	)

def get_data(file_name, interval_name, interval_api):

	print("\nPROC: Getting " + interval_name + " Interval Data...\n")

	df = create_frame(None)

	try:
		print("IO: Looking For Existing Data...")
		df = pandas.concat([df, pandas.read_csv(file_name)]).drop_duplicates(subset="Open Time").sort_values(by=["Open Time"]).reset_index(drop=True)
		start_time = df.iloc[-2]["Open Time"]
		print("Found!")
	except:
		print("WARN: No Existing Data Found!")
		start_time = 1512108000000
	end_time = int(round(time.time() * 1000))

	try:
		print("API: Get " + interval_name + " Interval Data...")

		while start_time < end_time:
			current_end = start_time + 259200000
			if start_time + 259200000 > end_time:
				current_end = end_time

			print("\tStart Time: " + str(start_time) + "\tEnd Time: " + str(current_end))

			df = pandas.concat([
				df,
				create_frame(client.get_historical_klines("ETHBTC", interval_api, str(start_time), str(current_end)))
			]).drop_duplicates(subset="Open Time").sort_values(by=["Open Time"]).reset_index(drop=True)
			start_time += 259200000
			time.sleep(4)
		print("Success!")
	except:
		print("ERROR: Failed API Call!")
		sys.exit()

	try:
		print("IO: Writing " + interval_name + " Interval Data to " + file_name)
		df.to_csv(file_name, index=False)
		print("Success!")
	except:
		print("ERROR: Failed Writing to File!")
		sys.exit()

get_data("data_hour.csv", "1-Hour", Client.KLINE_INTERVAL_1HOUR)