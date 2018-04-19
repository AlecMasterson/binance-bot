from binance.client import Client
import sys, utilities, pandas, datetime, time


# Create a DataFrame to store the historical data from the Binance API
# data - The initial data for the DataFrame
def create_frame(data):
    return pandas.DataFrame(data, columns=utilities.COLUMN_STRUCTURE)


# Concat two similar DataFrames, remove duplicates, and maintain the correct order
# df - First DataFrame
# df2 - Second DataFrame
def combine_frames(df, df2):
    return pandas.concat([df, df2]).drop_duplicates(subset=['Open Time']).sort_values(by=['Open Time']).reset_index(drop=True)


# Load the price-data DataFrame from a file, if of the correct column structure
# fileName - The csv file that contains the price-data
def load_file(fileName):
    priceData = pandas.read_csv(fileName)
    if list(priceData) != utilities.COLUMN_STRUCTURE: utilities.throw_error('Incorrect price-data DataFrame column structure')
    return priceData


# Update existing, or create new, price-data file.
# dir - The directory to read/write data from/to
# api - The specific time interval API to use
# coinpair - The coinpair to get data for
def get_data(dir, api, coinpair):
    try:
        df = create_frame(None)
        client = Client('', '')

        try:
            df = combine_frames(df, load_file(dir + str(coinpair) + '.csv'))        # Load currently stored historical data for the coinpair.
            startTime = df.iloc[-2]['Open Time']        # Get the second to last timestamp (allow some overlap), if it exists.
        except:
            utilities.throw_info('No Existing Data Found')
            startTime = datetime.datetime(2018, 1, 20).timestamp() * 1000        # If no existing data was found, use "Jan 20, 2018" in milliseconds as a default start datetime.
        endTime = datetime.datetime.now().timestamp() * 1000        # The end datetime will always be the current time in milliseconds.

        while startTime < endTime:
            curEnd = min(startTime + 259200000, endTime)        # Acquire data in 3 day intervals to not overload the API.

            df = combine_frames(df, create_frame(client.get_historical_klines(coinpair, api, str(startTime), str(curEnd))))

            startTime += 259200000        # Acquire data in 3 day intervals to not overload the API.
            time.sleep(2)        # Wait between API calls to not overload the API.

        df.to_csv(dir + str(coinpair) + '.csv', index=False)

    except Exception as e:
        print(e)
        utilities.throw_error('Unknown Error Getting Historical Data')


if __name__ == "__main__":

    # Inform the start of this script.
    utilities.throw_info('Get_History Script Starting')

    # Verify command usage.
    if len(sys.argv) != 1: utilities.throw_error('Command Usage -> \'python3 get_history.py [coinpair 1] [coinpair 2] ... [coinpair N]\'')

    # Get the default info for time intervals and coinpairs to use.
    locations = utilities.get_default_dirs_intervals()
    coinpairs = utilities.get_default_coinpairs()

    for location in locations:
        for coinpair in coinpairs:
            utilities.throw_info('Getting Data for ' + coinpair + ' coinpair in ' + location['dir'])
            get_data(location['dir'], location['api'], coinpair)
            utilities.throw_info('Done Getting Data for ' + coinpair + ' coinpair in ' + location['dir'])

    # Inform the end of this script
    utilities.throw_info('Get_History Script Completed')