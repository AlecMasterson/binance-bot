from binance.client import Client
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

import utilities


class Sockets:

    # Initialize a new Sockets with the required information
    # Start all socket connections used by the bot
    def __init__(self, client, data):
        self.client = client
        self.data = data

        # This handles all socket connections to Binance.
        self.manager = BinanceSocketManager(client)

        # Create a kline socket connection for each coinpair.
        for coinpair in utilities.COINPAIRS:

            # TODO: Remove this when not testing.
            if coinpair != 'ICXBTC': continue

            # The kline_socket connection consistently returns the latest price info for a coinpair.
            self.manager.start_kline_socket(coinpair, self.kline_callback, interval=Client.KLINE_INTERVAL_1MINUTE)

        # Start all socket connections.
        self.manager.start()

    # The kline socket connection handler
    # message - The response message from the socket connection
    def kline_callback(self, message):

        # Handle response errors from the connection.
        # If this fails, stop the bot.
        if message['e'] == 'error':
            self.close_socket_manager()
            utilities.throw_error('Error in kline Socket Connection', True)
        else:

            # If the most recent kline is complete, add a new Candle to the Coinpair.
            if message['k']['x']:

                # If the kline entry is the same as the most recent entry in the Coinpair, ignore it.
                # This may happen the first time this function is run, but never again.
                if message['k']['t'] == self.data[message['s']].data[-1].openTime: return

                self.data[message['s']].add_candle(Candle(message['k']['t'], message['k']['o'], message['k']['h'], message['k']['l'], message['k']['c'], message['k']['T']), True)

            # Use the bot's handler for handling new data.
            import bot
            bot.new_data(message)

    # Close the websocket manager, which will end all socket connections
    def close_socket_manager(self):

        # Attempt to close the websocket manager gracefully.
        # If this fails, reactor.stop() will force close the connections.
        try:
            self.manager.close()
            utilities.throw_info('Socket Manager Closed')
        except:
            utilities.throw_info('Failed to Gracefully Close Socket Manager')

        # Force close the socket connection.
        reactor.stop()
