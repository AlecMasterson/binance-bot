from binance.client import Client
import pandas, sys, time, datetime

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

# Create a pandas.DataFrame to store historical data from Binance API
def create_frame(data):
	return pandas.DataFrame(
		data,
		columns=[
			'Open Time', 'Open', 'High', 'Low',
			'Close', 'Volume', 'Close Time', 'Quote Asset Volume',
			'Number Trades', 'Taker Base Asset Volume',
			'Take Quote Asset Volume', 'Ignore'
		]
	)

# Concat two similar pandas.DataFrame structures and maintain the correct order
def combine_frames(df, df2):
	return pandas.concat(
		[df, df2]
	).drop_duplicates(
		subset=['Open Time']
	).sort_values(
		by=['Open Time']
	).reset_index(drop=True)

# ------------------------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------------------------

def get_data(coin, client, api):

	# --------------------------------------------------------------------------
	# PREVIOUSLY STORED DATA
	# --------------------------------------------------------------------------

	df = create_frame(None)
	try:
		print('IO: Looking For Existing Data...')
		df = combine_frames(df, pandas.read_csv('data_new/'+str(coin)+'.csv'))
		startTime = df.iloc[-2]['Open Time']
		print('Found! Pulling New Historical Data...')
	except:
		print('WARN: No Existing Data Found! Pulling Historical Data...')
		# Use Jan 20, 2018 as a default start date.
		startTime = 1516406400000
	endTime = int(round(time.time() * 1000))

	# --------------------------------------------------------------------------
	# GET NEW DATA
	# --------------------------------------------------------------------------

	try:
		while startTime < endTime:
			# Acquire data in 3 day intervals to not overload the API.
			curEnd = min(startTime + 259200000, endTime)

			formatStart = str(datetime.datetime.fromtimestamp(startTime / 1e3))
			formatEnd = str(datetime.datetime.fromtimestamp(curEnd / 1e3))
			print('\tStart Time: ' + formatStart + '\tEnd Time: ' + formatEnd)

			df = combine_frames(
				df, create_frame(
					client.get_historical_klines(
						coin, api,
						str(startTime), str(curEnd)
					)
				)
			)

			# Acquire data in 3 day intervals to not overload the API.
			startTime += 259200000

			# Wait between API calls to not overload the API.
			time.sleep(3)
	except:
		print('ERROR: Failed API Call!\n')
		sys.exit()

	# --------------------------------------------------------------------------
	# SAVE DATA
	# --------------------------------------------------------------------------

	try:
		df.to_csv('data_new/'+str(coin)+'.csv', index=False)
	except:
		print('ERROR: Failed Writing to File!\n')
		sys.exit()



# ------------------------------------------------------------------------------



if __name__ == "__main__":

	# --------------------------------------------------------------------------
	# COMMAND USAGE VERIFICATION
	# --------------------------------------------------------------------------

	if len(sys.argv) > 1:
		print('\nERROR: Command Usage -> \'python3 get_history.py\'\n')
		sys.exit()

	print('\nPROC: Getting Historical Data')

	# --------------------------------------------------------------------------
	# SETUP
	# --------------------------------------------------------------------------

	try:
		client = Client('', '')
	except:
		print('ERROR: Could Not Connect to API Client!\n')
		sys.exit()

	# Manually edit this for different time intervals.
	api = Client.KLINE_INTERVAL_1HOUR

	# Manually edit this for different coin pairs.
	coins = [
		'ETHBTC', 'BNBBTC', 'XRPBTC', 'LTCBTC', 'ADABTC', 'EOSBTC', 'XLMBTC'
	]
	for coin in coins:
		print('\nINFO: Getting Data for '+coin+' CoinPair')
		get_data(coin, client, api)
		print('\nINFO: Done Getting Data for '+coin+' CoinPair')

	print('\nPROC: Done!\n')