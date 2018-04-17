from binance.client import Client
import pandas, sys, time, datetime

columnStructure = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number Trades', 'Taker Base Asset Volume', 'Take Quote Asset Volume', 'Ignore']


# Create a DataFrame to store the historical data from the Binance API
# data - The initial data for the DataFrame
def create_frame(data):
    return pandas.DataFrame(
        data, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number Trades', 'Taker Base Asset Volume', 'Take Quote Asset Volume', 'Ignore'])


# Concat two similar DataFrames, remove duplicates, and maintain the correct order
# df - First DataFrame
# df2 - Second DataFrame
def combine_frames(df, df2):
    return pandas.concat([df, df2]).drop_duplicates(subset=['Open Time']).sort_values(by=['Open Time']).reset_index(drop=True)


# Load the price-data DataFrame from a file, if of the correct column structure
# fileName - The csv file that contains the price-data
def load_file(fileName):
    priceData = pandas.read_csv(fileName)
    if list(priceData) != columnStructure:
        print('ERROR: Incorrect price-data DataFrame column structure!')
        sys.exit()
    return priceData


# Update existing, or create new, price-data file.
# dir - The directory to read/write data from/to
# api - The specific time interval API to use
# coinPair - The coinPair to get data for
def get_data(dir, api, coinPair):
    try:
        df = create_frame(None)
        client = Client('', '')

        try:
            df = combine_frames(df, load_file(dir + str(coinPair) + '.csv'))        # Load currently stored historical data for the coinPair.
            startTime = df.iloc[-2]['Open Time']        # Get the second to last timestamp (allow some overlap), if it exists.
        except:
            startTime = datetime.datetime(2018, 1, 20).timestamp() * 1000        # If no existing data was found, use "Jan 20, 2018" in milliseconds as a default start datetime.
        endTime = datetime.datetime.now().timestamp() * 1000        # The end datetime will always be the current time in milliseconds.

        while startTime < endTime:
            curEnd = min(startTime + 259200000, endTime)        # Acquire data in 3 day intervals to not overload the API.

            formatStart = str(datetime.datetime.fromtimestamp(startTime / 1e3))
            formatEnd = str(datetime.datetime.fromtimestamp(curEnd / 1e3))
            print('\tStart Time: ' + formatStart + '\tEnd Time: ' + formatEnd)

            df = combine_frames(df, create_frame(client.get_historical_klines(coinPair, api, str(startTime), str(curEnd))))

            startTime += 259200000        # Acquire data in 3 day intervals to not overload the API.
            time.sleep(3)        # Wait between API calls to not overload the API.

        df.to_csv(dir + str(coinPair) + '.csv', index=False)

    except:
        print('ERROR: Unknown Error Getting Historical Data!')
        sys.exit()


if __name__ == "__main__":

    print('INFO: Command Usage -> \'python3 get_history.py [CoinPair 1] [CoinPair 2] ... [CoinPair N]\'\n')

    locations = [{
        'dir': 'data_15_min/',
        'api': Client.KLINE_INTERVAL_15MINUTE
    }, {
        'dir': 'data_30_min/',
        'api': Client.KLINE_INTERVAL_30MINUTE
    }, {
        'dir': 'data_1_hour/',
        'api': Client.KLINE_INTERVAL_1HOUR
    }, {
        'dir': 'data_2_hour/',
        'api': Client.KLINE_INTERVAL_2HOUR
    }]

    coinPairs = sys.argv[1:]
    for coinPair in ['ADAETH', 'BNBBTC', 'BNBETH', 'ETHBTC', 'XRPETH']:
        if not coinPair in coinPairs: coinPairs.append(coinPair)

    for location in locations:
        for coinPair in coinPairs:
            print('INFO: Getting Data for ' + coinPair + ' CoinPair in ' + location['dir'])
            get_data(location['dir'], location['api'], coinPair)
            print('INFO: Done Getting Data for ' + coinPair + ' CoinPair in ' + location['dir'])
