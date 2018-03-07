from binance.client import Client
import pandas
import sys, time

try:
	client = Client("", "")
except:
	print("ERROR: Could Not Connect to API Client!")
	sys.exit()

def get_data(file_name, interval_name, interval_api):
	
	print("\nPROC: Getting " + interval_name + " Interval Data...\n")
	
	try:
		print("IO: Looking For Existing Data...")
		frame_old = pandas.read_csv(file_name)
		start_time = frame_old.iloc[-1]["Open Time"]
		print("Found!")
	except:
		print("WARN: No Existing Data Found!")
		start_time = "1 Dec, 2017"
	end_time = str(int(round(time.time() * 1000)))

	try:
		print("API: Get " + interval_name + " Interval Data...")
		data = client.get_historical_klines("ETHBTC", interval_api, str(start_time), str(end_time))
		frame = pandas.DataFrame(
			data,
			columns=[
				"Open Time", "Open", "High", "Low",
				"Close", "Volume", "Close Time", "Quote Asset Volume",
				"Number Trades", "Taker Base Asset Volume", "Take Quote Asset Volume", "Ignore"
			]
		)
		try:
			frame_old
			frame = pandas.concat([frame, frame_old]).drop_duplicates(subset="Open Time").sort_values(by=["Open Time"]).reset_index(drop=True)
		except:
			frame_old = None
		print("Success!")
	except:
		print("ERROR: Failed API Call!")
		sys.exit()

	try:
		print("IO: Writing " + interval_name + " Interval Data to " + file_name)
		frame.to_csv(file_name, index=False)
		print("Success!")
	except:
		print("ERROR: Failed Writing to File!")
		sys.exit()
	
get_data("data_minute.csv", "30-Minute", Client.KLINE_INTERVAL_30MINUTE)
get_data("data_hour.csv", "1-Hour", Client.KLINE_INTERVAL_1HOUR)