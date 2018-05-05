from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
import sys, time, pandas, numpy, talib
import utilities


# Close the websocket manager, which will end all connections
# manager - The websocket manager object
def close_socket_manager(manager):
    # Attempt to close the websocket manager gracefully.
    # If this fails, sys.exit() will force close the connection.
    try:
        manager.close()
        utilities.throw_info('Socket Manager Closed')
    except:
        utilities.throw_info('Could Not Gracefully Close Socket Manager')


# Update the overhead information associated with a coinpair
# This information is what's used to determine if a buy/sell order is needed
# coinpair - The coinpair needing updating
def update_overhead(coinpair):
    # Access the global variables storing all price data and overhead information from all coinpairs.
    global data
    global overhead

    # Convert data to type float for the talib library.
    floatData = [float(x) for x in data[coinpair]['Close']]

    # Extremely small numbers (prices) break talib calculations, we must multiply and then divide by 1e6.
    macd, macdsignal, macdhist = talib.MACDFIX(numpy.array(floatData) * 1e6, signalperiod=9)
    upperband, middleband, lowerband = talib.BBANDS(numpy.array(floatData) * 1e6, timeperiod=14, nbdevup=2, nbdevdn=2, matype=0)
    overhead[coinpair] = {'macd': macd / 1e6}
    overhead[coinpair]['lowerband'] = lowerband / 1e6


# Update the pandas.DataFrame containing all coinpair price data
# This is run when a kline entry has been marked complete by the socket connection
# info - Kline information returned from the kline socket connection
def update_data(info):
    # Access the global variable storing all price data from all coinpairs.
    global data

    # If the kline entry is the same as the most recent pandas.DataFrame entry, ignore it.
    # This happens the first time this function is run, but never again.
    if info['k']['t'] == data[info['s']].iloc[-1]['Open Time']:
        return

    # Append the new necessary information onto the end of the pandas.DataFrame object.
    data[info['s']] = data[info['s']].append(
        {
            'Open Time': info['k']['t'],
            'Open': info['k']['o'],
            'High': info['k']['h'],
            'Low': info['k']['l'],
            'Close': info['k']['c'],
            'Close Time': info['k']['T']
        }, ignore_index=True)

    update_overhead(info['s'])


# The kline_socket connection handler
# message - The response message from the kline socket connection
def kline_callback(message):
    # Handle response errors from the connection.
    if message['e'] == 'error':
        utilities.throw_info('Error in kline_socket')
    else:
        # If the most recent kline is complete, update the global data pandas.DataFrame.
        if message['k']['x']: update_data(message)


if __name__ == "__main__":

    # Command Usage Verification
    if len(sys.argv) != 1: utilities.throw_error('Command Usage -> \'python3 sockets.py\'', True)

    # Connect to the Binance API using our public and secret keys.
    try:
        client = Client('lfeDDamF6ckP7A2uWrd7uJ5nV0aJedQwD2H0HGujNuxmGgtyQQt0kL3lS6UFlRLS', 'phpomS4lCMKuIxF0BgrP4d5N9rEPzf8Dy4ZRVjJ0XeO4Wn7PmOC7uhYsyypi9gFJ')
    except:
        utilities.throw_error('Could Not Connect to Binance API', True)

    # Acquire all necessary asset balances from the API.
    try:
        balances = []

        # TODO: Do this. Fix the get_account API synchronization issue.
        print('TODO: Get Asset Balances...')
    except:
        utilities.throw_error('Failed to Get Asset Balances', True)

    # Acquire all necessary historical data from the API for each coinpair.
    try:
        data = {}
        overhead = {}
        for coinpair in utilities.COINPAIRS:

            # TODO: Remove this when not testing.
            if coinpair != 'ICXBTC': continue

            data[coinpair] = pandas.DataFrame(client.get_klines(symbol=coinpair, interval=Client.KLINE_INTERVAL_1MINUTE), columns=utilities.COLUMN_STRUCTURE)
            update_overhead(coinpair)

            # Wait between API calls to not overload the API.
            time.sleep(1)
    except:
        utilities.throw_error('Failed to Get Price Data', True)

    # Create the websocket manager and all necessary connections.
    try:
        manager = BinanceSocketManager(client)

        # Create a kline_socket connection for each coinpair.
        for coinpair in utilities.COINPAIRS:

            # TODO: Remove this when not testing.
            if coinpair != 'ICXBTC': continue

            manager.start_kline_socket(coinpair, kline_callback, interval=Client.KLINE_INTERVAL_1MINUTE)

        manager.start()
    except:
        close_socket_manager(manager)
        utilities.throw_error('Could Not Start Socket Manager', True)

    # TODO: Import current positions.
    positions = []

    # Run the rest of the script infinitely!
    while True:

        # Get all current open orders, unfortunately the API endpoint goes one coinpair at a time.
        # If there's an issue getting the open orders, restart the infinite loop and try again.
        try:
            orders = []
            for coinpair in utilities.COINPAIRS:

                # TODO: Remove this when not testing.
                if coinpair != 'ICXBTC': continue

                for order in client.get_all_orders(symbol=coinpair):
                    orders.append(order)

                # Wait between API calls to not overload the API.
                time.sleep(1)

            # TODO: Update positions with latest order information.

            # TODO: Export current positions.

        except:
            utilities.throw_error('Failed to Get Open Orders', False)
            continue

        # TODO: Determine if selling.

        # TODO: Make a sell order to the API if necessary.

        # Determine if buying.

        # TODO: Make a buy order to the API if necessary.

        # Cool debugging output to watch the socket connection.
        print(data['ICXBTC'][['Open Time', 'Open', 'High', 'Low', 'Close']].tail(2))
        print(overhead['ICXBTC']['macd'][-2:])
        print(overhead['ICXBTC']['lowerband'][-2:])
        print('\n')

        # Stall the infinite loop for obvious reasons.
        time.sleep(5)
