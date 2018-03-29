import pandas, sys
from datetime import datetime, timedelta

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

# Convert a millisecond time to a datetime object
def to_datetime(milli):
	return datetime.fromtimestamp(milli / 1e3)

# Get the next Saturday after 'curDate'
def next_saturday(curDate):
	return (
		curDate + timedelta((12 - curDate.weekday()) % 7)
	).replace(hour=23, minute=59, second=59)

# Get the index # in 'weekData' where 'date' fell
def get_week(weekData, date):
	for index, row in weekData.iterrows():
		if date > row['startDate'] and date < row['endDate']:
			return index

# Return the total (in BTC) value of the wallet
def total_wallet(trade):
	return trade['btc'] + (trade['eth'] * trade['price'])

# ------------------------------------------------------------------------------
# COMMAND USAGE VERIFICATION
# ------------------------------------------------------------------------------

if len(sys.argv) is not 3:
	print(
		'\nERROR: Command Usage ->' +
		'\'python3 analyze.py <price-data> <trade-data>\'\n'
	)
	sys.exit()

print('\nPROC: Analyze Trading Data From ' + sys.argv[2] + '\n')

# ------------------------------------------------------------------------------
# SETUP
# ------------------------------------------------------------------------------

try:
	print('IO: Looking For Price Data...')
	priceData = pandas.read_csv(sys.argv[1])
	print('Found!\n')
except:
	print('ERROR: No Price Data Found!\n')
	sys.exit()

try:
	print('IO: Looking For Trade Data...')
	tradeData = pandas.read_csv(sys.argv[2])
	print('Found!\n')
except:
	print('ERROR: No Trade Data Found!\n')
	sys.exit()

# ------------------------------------------------------------------------------
# INITIAL ANALYSIS
# ------------------------------------------------------------------------------

if len(tradeData.index) == 1:
	print('ERROR: Trade Data Empty!\n')
	sys.exit()

# Get the start/end dates that trading was done on.
startDate = to_datetime(priceData.iloc[0]['Open Time'])
endDate = to_datetime(priceData.iloc[-1]['Open Time'])

# Get the start/end wallet values and the % change.
startWallet = total_wallet(tradeData.iloc[1])
endWallet = total_wallet(tradeData.iloc[-1])
walletChange = endWallet / startWallet * 100

# ------------------------------------------------------------------------------
# EMPTY DATAFRAME OF WEEKS TRADED
# ------------------------------------------------------------------------------

# This section creates a DataFrame with the column structure of 'curWeek' below.
# Each row will represent a calendar week and the trades inside it.
# We assume a week to be Sunday (startDate) to Saturday (endDate).
# We store how many trades occur and the value of our wallet before and after.

# Temp variable to hold the individual week information.
weeks = []

curWeek = {
	'startDate': startDate, 'endDate': next_saturday(startDate),
	'numTrades': 0, 'startWallet': -1.0, 'endWallet': -1.0
}
for index, row in priceData.iterrows():
	if index > 0:
		curDate = to_datetime(row['Open Time'])
		if curDate.weekday() == 6 and to_datetime(
			priceData.iloc[index - 1]['Open Time']
		).weekday() == 5:
			weeks.append(curWeek)
			curWeek = {
				'startDate': curDate, 'endDate': next_saturday(curDate),
				'numTrades': 0, 'startWallet': -1.0, 'endWallet': -1.0
			}
weeks.append(curWeek)

weekData = pandas.DataFrame(weeks)

# ------------------------------------------------------------------------------
# WEEKLY TRADING STATISTICS
# ------------------------------------------------------------------------------

# This section goes through our 'tradeData' to populate our DataFrame.
# Please refer to above description this DataFrame structure.

for index, row in tradeData.iterrows():
	if index > 0:
		week = get_week(weekData, to_datetime(row['time']))
		if weekData.iloc[week]['startWallet'] == -1:
			weekData.at[week, 'startWallet'] = total_wallet(row)
			weekData.at[week, 'endWallet'] = total_wallet(row)
			weekData.at[week, 'numTrades'] += 1
		else:
			weekData.at[week, 'endWallet'] = total_wallet(row)
			weekData.at[week, 'numTrades'] += 1

# Finally, calculate the average weekly percent ROI.

percentChanges = []
total = 0.0
for index, row in weekData.iterrows():
	if row['numTrades'] > 0:
		percentChange = (row['endWallet'] / row['startWallet']) - 1.0
		total += percentChange
		percentChanges.append(percentChange)

averagePercentChange = total / len(weekData.index) * 100

# ------------------------------------------------------------------------------
# OUTPUT
# ------------------------------------------------------------------------------

print('RESULTS...\n\nStart Date: %s\t\tEnd Date: %s' % (startDate, endDate))
print('Start Wallet: %.5f\t\t\tEnd Wallet: %.5f' % (startWallet, endWallet))
print(
	'%.5f%% ROI Over %s, hours' %
	(walletChange, str(endDate-startDate))
)
print('%.5f%% Average Weekly ROI\n' % averagePercentChange)

print('PROC: Done!\n')