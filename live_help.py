from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
from twisted.internet import reactor
import sys, time, pandas, talib, numpy, glob
import utilities, live


# Close the websocket manager, which will end all connections
# manager - The websocket manager object
def close_socket_manager(manager):

    # Attempt to close the websocket manager gracefully.
    # If this fails, sys.exit() will force close the connection.
    try:
        manager.close()
        utilities.throw_info('Socket Manager Closed')
    except:
        utilities.throw_info('Failed to Gracefully Close Socket Manager')

    # Force close the socket connection.
    reactor.stop()


# Update the balances dictionary with the current account balances
# manager - The websocket manager object
# client - The Binance client object
# balances - The balances dictionary
def update_balances(manager, client, balances):

    # Attempt to update the dictionary with the current available (free) amount for each asset.
    # If this fails, stop the bot.
    try:
        # Do the base currency separately, then do all the coinpairs.
        balances['BTC'] = client.get_asset_balance(asset='BTC')['free']

        # Wait between API calls to not overload the API.
        time.sleep(1)

        for coinpair in utilities.COINPAIRS:

            # TODO: Remove this when not testing.
            if coinpair != 'ICXBTC': continue

            # I.E. If the coinpair was 'POWRBTC', then coinpair[:-3] returns 'POWR'.
            balances[coinpair[:-3]] = client.get_asset_balance(asset=coinpair[:-3])['free']

            # Wait between API calls to not overload the API.
            time.sleep(1)
    except:
        close_socket_manager(manager)
        utilities.throw_error('Failed to Update Asset Balances', True)


# Update the overhead information associated with a coinpair
# This information is what's used to determine if a buy/sell order is needed
# data - Contains all historical data of all coinpairs
# overhead - Contains the current overhead information associatedwith all coinpairs
# coinpair - The coinpair that is being updated
def update_overhead(data, overhead, coinpair):

    # Convert data to type float for the talib library.
    floatData = [float(x) for x in data[coinpair]['Close']]

    # Extremely small numbers (prices) break talib calculations, we must multiply and then divide by 1e6.
    macd, macdsignal, macdhist = talib.MACDFIX(numpy.array(floatData) * 1e6, signalperiod=9)
    upperband, middleband, lowerband = talib.BBANDS(numpy.array(floatData) * 1e6, timeperiod=14, nbdevup=2, nbdevdn=2, matype=0)
    overhead[coinpair] = {'macd': macd / 1e6}
    overhead[coinpair]['lowerband'] = lowerband / 1e6


# Update the DataFrame containing all historical data for a specific coinpair
# This is run when a kline entry has been marked complete by the socket connection
# info - Returned kline information from the socket connection
def update_data(info):

    # Since this function is called via a socket connection callback function, we must use a global.
    # This global variable contains all historical data of all coinpairs
    global data

    # If the kline entry is the same as the most recent entry in data, ignore it.
    # This happens the first time this function is run, but never again.
    if info['k']['t'] == data[info['s']].iloc[-1]['Open Time']:
        return

    # Append the new necessary information onto the end of the DataFrame object.
    # Each entry in the data Dictionary is a DataFrame for a specific coinpair.
    data[info['s']] = data[info['s']].append(
        {
            'Open Time': info['k']['t'],
            'Open': info['k']['o'],
            'High': info['k']['h'],
            'Low': info['k']['l'],
            'Close': info['k']['c'],
            'Close Time': info['k']['T']
        }, ignore_index=True)

    # Update the overhead information with the new data.
    update_overhead(info['s'])


# The socket connection handler for kline data
# message - The response message from the socket connection
def kline_callback(message):

    # Since this function is the socket connection callback function, we must use a global.
    # This global variable is the websocket manager object.
    global manager

    # Handle response errors from the connection.
    # If this fails, stop the bot.
    if message['e'] == 'error':
        close_socket_manager(manager)
        utilities.throw_error('Error in kline Socket Connection', True)
    else:

        # If the most recent kline is complete, update data DataFrame.
        if message['k']['x']: update_data(message)

        # Use the bot's handler for handling new data.
        live.new_data()


# This is the initial function to prepare all necessary info for the bot.
# All initial Binance API calls for setup are done here.
# If anything here fails, a forced exit of the bot is necessary.
def initialize():

    # Command Usage Verification
    if len(sys.argv) != 1: utilities.throw_error('Command Usage -> \'python3 live.py\'', True)

    # Connect to the Binance API using our public and secret keys.
    try:
        client = Client('lfeDDamF6ckP7A2uWrd7uJ5nV0aJedQwD2H0HGujNuxmGgtyQQt0kL3lS6UFlRLS', 'phpomS4lCMKuIxF0BgrP4d5N9rEPzf8Dy4ZRVjJ0XeO4Wn7PmOC7uhYsyypi9gFJ')
    except:
        utilities.throw_error('Failed to Connect to Binance API', True)
    utilities.throw_info('Successfully Connected to Binance Client')

    # Acquire all necessary historical data from the API for each coinpair.
    try:
        data = {}
        overhead = {}
        for coinpair in utilities.COINPAIRS:

            # TODO: Remove this when not testing.
            if coinpair != 'ICXBTC': continue

            # Query the API for the latest 1000 entry points and then update the overhead associated.
            data[coinpair] = pandas.DataFrame(client.get_klines(symbol=coinpair, interval=Client.KLINE_INTERVAL_1MINUTE), columns=utilities.COLUMN_STRUCTURE)
            update_overhead(data, overhead, coinpair)

            # Wait between API calls to not overload the API.
            time.sleep(1)
    except:
        utilities.throw_error('Failed to Get Price Data', True)
    utilities.throw_info('Successfully Finished Getting Historical Data')

    # Acquire all Binance specific information related to each coinpair.
    try:
        symbols = {}
        for coinpair in utilities.COINPAIRS:

            # TODO: Remove this when not testing.
            if coinpair != 'ICXBTC': continue

            # Query the API for specific trade info for each coinpair.
            symbols[coinpair] = client.get_symbol_info(coinpair)

            # Wait between API calls to not overload the API.
            time.sleep(1)
    except:
        utilities.throw_error('Failed to Get Symbol Info', True)
    utilities.throw_info('Successfully Finished Getting Symbol Info')

    # Create the websocket manager and all necessary connections.
    try:
        manager = BinanceSocketManager(client)

        # Create a kline_socket connection for each coinpair.
        for coinpair in utilities.COINPAIRS:

            # TODO: Remove this when not testing.
            if coinpair != 'ICXBTC': continue

            # The kline_socket connection consistently returns the latest price info for a coinpair.
            manager.start_kline_socket(coinpair, kline_callback, interval=Client.KLINE_INTERVAL_1MINUTE)

        manager.start()
    except:
        utilities.throw_error('Failed to Start Socket Manager', True)
    utilities.throw_info('Successfully Completed WebSocket Connections')

    # Import saved positions from previous bot usages.
    # This holds all positions, open or closed, that this bot has created.
    try:
        # Read the previously exported CSV file if it exists, otherwise use a new DataFrame.
        if len(glob.glob('positions.csv')) == 1:
            positions = pandas.read_csv('positions.csv')
        else:
            positions = pandas.DataFrame(None, columns=utilities.POSITION_STRUCTURE)

        # Be sure that the column structure is correct after importing the positions.
        if list(positions) != utilities.POSITION_STRUCTURE:
            close_socket_manager(manager)
            utilities.throw_error('Positions Column Structure is Incorrect', True)
    except:
        close_socket_manager(manager)
        utilities.throw_error('Failed to Import Positions', True)
    utilities.throw_info('Successfully Imported Positions')

    # This is used to store the available value for all assets being used.
    balances = {}
    update_balances(manager, client, balances)

    # Return all necessary initialized information to the bot itself.
    return client, data, overhead, symbols, manager, positions, balances


# Use this to run this script as a stand-alone script.
# This script is useless on it's own but is helpful in debugging.
if __name__ == "__main__":
    client, data, overhead, symbols, manager, positions, balances = initialize()
    utilities.throw_info('Successfully Completed Initialization')

    # Close all socket connections and stop the script.
    close_socket_manager(manager)
