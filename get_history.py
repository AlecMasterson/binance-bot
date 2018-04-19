from binance.client import Client
import sys, utilities, pandas, datetime, time, numpy


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
    if list(priceData) != utilities.COLUMN_STRUCTURE: utilities.throw_error('Incorrect price-data DataFrame column structure', True)
    return priceData


# Update existing, or create new, price-data file. Return True if successful.
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

    except:
        utilities.throw_error('Unknown Error Getting Historical Data', False)
        return {'status': False, 'frame': df}

    return {'status': True, 'frame': df}


# The main functionality of get_history wrapped into a single function
# locations - The location or locations to focus on
def execute(locations):
    # Inform the start of this script.
    utilities.throw_info('Get_History Script Starting')

    # Verify we have directories to check.
    if len(locations) == 0: utilities.throw_error('No Locations Found', True)

    # Get the default coinpairs to use.
    coinpairs = utilities.get_default_coinpairs()

    results = []
    for location in locations:
        combined = []        # Stores all coinpair DataFrames from a single time interval.
        for coinpair in coinpairs:
            utilities.throw_info('Getting Data for ' + coinpair + ' coinpair in ' + location['dir'])

            # Append whether the retreival was succesful.
            result = get_data(location['dir'], location['api'], coinpair)
            results.append(result['status'])

            # Strip down the resulting DataFrame so it can be merged with all the coinpair DataFrames.
            try:
                result['frame'].set_index('Open Time', inplace=True)
                result['frame'] = result['frame'].drop(columns=['Volume', 'Quote Asset Volume', 'Number Trades', 'Taker Base Asset Volume', 'Take Quote Asset Volume', 'Ignore'])
                result['frame'] = result['frame'].rename(columns={
                    'Open': 'open-' + coinpair,
                    'High': 'high-' + coinpair,
                    'Low': 'low-' + coinpair,
                    'Close': 'close-' + coinpair,
                    'Close Time': 'cTime-' + coinpair
                })
                combined.append(result['frame'])
            except:
                utilities.throw_error('Failed to Strip DataFrame for Merging', False)
                results.append(False)

        # Merge all the coinpair DataFrames.
        try:
            for i in range(len(combined)):
                if i == 0: continue
                combined[0] = pandas.merge(combined[0], combined[i], left_index=True, right_index=True, how='outer')

            # Fill in missing data that could cause inconsistencies between coinpairs and then write to 'ALL.csv'.
            combined[0] = combined[0].replace(numpy.nan, numpy.nan).ffill()
            combined[0].to_csv(location['dir'] + 'ALL.csv')
        except:
            utilities.throw_error('Failed to Merge DataFrames', False)
            results.append(False)

    # Check if any of the data wasn't received successfully.
    message = 'Get_History Script Completed'
    if False in results: message += ' with Errors'

    # Inform the end of this script
    utilities.throw_info(message)

    if False in results: return False
    return True


if __name__ == "__main__":

    # Verify command usage before executing.
    if len(sys.argv) != 1: utilities.throw_error('Command Usage -> \'python3 get_history.py\'', True)

    # Use the default time intervals.
    execute(utilities.get_default_dirs_intervals())
