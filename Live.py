from binance.client import Client

import sys, time, pandas, glob
import utilities

from Coinpair import Coinpair
from Candle import Candle
from Sockets import Sockets
from Position import Position
from Balance import Balance


class Live:

    # Initialize a new Live object, which is the framework to the live bot
    def __init__(self):

        # Connect to the Binance API using our public and secret keys.
        try:
            self.client = Client('lfeDDamF6ckP7A2uWrd7uJ5nV0aJedQwD2H0HGujNuxmGgtyQQt0kL3lS6UFlRLS', 'phpomS4lCMKuIxF0BgrP4d5N9rEPzf8Dy4ZRVjJ0XeO4Wn7PmOC7uhYsyypi9gFJ')
        except:
            utilities.throw_error('Failed to Connect to Binance API', True)
        utilities.throw_info('Successfully Connected to Binance Client')

        # Acquire all necessary historical data from the API for each coinpair.
        try:
            self.data = {}
            for coinpair in utilities.COINPAIRS:

                # TODO: Remove this when not testing.
                if coinpair != 'ICXBTC': continue

                # Instantiate a new Coinpair object for this coinpair.
                self.data[coinpair] = Coinpair(coinpair)

                # Query the API for the latest 1000 entry points.
                tempData = pandas.DataFrame(self.client.get_klines(symbol=coinpair, interval=Client.KLINE_INTERVAL_1MINUTE), columns=utilities.COLUMN_STRUCTURE)

                # Create a Candle and add it to the Coinpair for each entry returned by the API.
                for index, candle in tempData.iterrows():
                    self.data[coinpair].add_candle(Candle(candle['Open Time'], candle['Open'], candle['High'], candle['Low'], candle['Close'], candle['Close Time']), False)

                # Update the overhead information for this Coinpair.
                self.data[coinpair].update_overhead()

                # Add the specific information associated with this coinpair.
                self.data[coinpair].add_info(self.client.get_symbol_info(coinpair))

                # Wait between API calls to not overload the API.
                time.sleep(1)
        except:
            utilities.throw_error('Failed to Get Historical Data', True)
        utilities.throw_info('Successfully Finished Getting Historical Data')

        # Create the websocket manager and all necessary connections.
        try:
            self.sockets = Sockets(self.client, self.data)
        except:
            utilities.throw_error('Failed to Start Socket Manager', True)
        utilities.throw_info('Successfully Completed WebSocket Connections')

        # Import saved positions from previous bot usages.
        # This holds all positions, open or closed, that this bot has created.
        # TODO: Do this.
        self.positions = []

        # This contains the available value for all assets being used.
        self.balances = {}
        self.update_balances()
        utilities.throw_info('Successfully Updated Asset Balances')

        # This contains all live orders that have not been filled or cancelled yet.
        self.orders = []

    # Acquire the available value for all assets being used.
    def update_balances(self):
        try:
            for coinpair in utilities.COINPAIRS:
                self.balances[coinpair] = Balance(self.client, coinpair[:-3])

                # Wait between API calls to not overload the API.
                time.sleep(1)

            # Can't forget the base asset.
            self.balances['BTC'] = Balance(self.client, 'BTC')

            # Wait between API calls to not overload the API.
            time.sleep(1)
        except:
            self.sockets.close_socket_manager()
            utilities.throw_error('Failed to Update Asset Balances', True)

    # Use an order sent to Binance to create a new position for local tracking
    # This will only happen if an order is completely or partially filled
    # order - A returned order object from the API
    def create_position(self, order):

        # Notify the user of a new position.
        utilities.throw_info('New Position Added\n')
