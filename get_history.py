from binance.client import Client
import pandas, sys, time, datetime

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

# Create a frame to store historical data from API
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

# Concat two similar pandas.DataFrame and maintain the correct order
def combine_frames(df, df2):
	return pandas.concat(
		[df, df2]
	).drop_duplicates(
		subset='Open Time'
	).sort_values(
		by=['Open Time']
	).reset_index(drop=True)

# ------------------------------------------------------------------------------
# COMMAND USAGE VERIFICATION
# ------------------------------------------------------------------------------

if len(sys.argv) is not 2 and len(sys.argv) is not 3:
	print(
		'\nERROR: Command Usage ->' +
		'\'python3 get_history.py <output-file> [start-date]\'\n'
	)
	sys.exit()

print('\nPROC: Getting Historical Data\n')

# ------------------------------------------------------------------------------
# SETUP
# ------------------------------------------------------------------------------

try:
	client = Client('', '')
except:
	print('ERROR: Could Not Connect to API Client!\n')
	sys.exit()

# Manually edit this for different time intervals.
# Follow the specification detailed in the README file.
api = Client.KLINE_INTERVAL_1HOUR

# ------------------------------------------------------------------------------
# PREVIOUSLY STORED DATA
# ------------------------------------------------------------------------------

df = create_frame(None)
try:
	print('IO: Looking For Existing Data...')
	df = combine_frames(df, pandas.read_csv(sys.argv[1]))
	startTime = df.iloc[-2]['Open Time']
	print('Found!')
except:
	print('WARN: No Existing Data Found!')
	if len(sys.argv) is 2:
		# Use Dec 1, 2017 as a default start date.
		startTime = 1512108000000
	else:
		startTime = int(sys.argv[2])
endTime = int(round(time.time() * 1000))

# ------------------------------------------------------------------------------
# GET NEW DATA
# ------------------------------------------------------------------------------

try:
	print('API: Get Historical Data...')

	while startTime < endTime:
		# Acquire data in 3 day intervals to not overload the API.
		curEnd = min(startTime + 259200000, endTime)

		formatStart = str(datetime.datetime.fromtimestamp(startTime / 1e3))
		formatEnd = str(datetime.datetime.fromtimestamp(curEnd / 1e3))
		print('\tStart Time: ' + formatStart + '\tEnd Time: ' + formatEnd)

		df = combine_frames(
			df, create_frame(
				client.get_historical_klines(
					'ETHBTC', api,
					str(startTime), str(curEnd)
				)
			)
		)

		# Acquire data in 3 day intervals to not overload the API.
		startTime += 259200000

		# Wait between API calls to not overload the API.
		time.sleep(4)
	print('Success!')
except Exception as e:
	print(e)
	print('ERROR: Failed API Call!\n')
	sys.exit()

# ------------------------------------------------------------------------------
# SAVE DATA
# ------------------------------------------------------------------------------

try:
	print('IO: Writing Historical Data to ' + sys.argv[1])
	df.to_csv(sys.argv[1], index=False)
	print('Success!\n')
except:
	print('ERROR: Failed Writing to File!\n')
	sys.exit()

print('PROC: Done!\n')