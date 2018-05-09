from binance.client import Client

import sys, time, pandas, glob, csv
import utilities

from Coinpair import Coinpair
from Candle import Candle
from Sockets import Sockets
from Position import Position
from Balance import Balance
from Order import Order


class Live:

    # Initialize a new Live object, which is the framework to the live bot
    def __init__(self):

        # Connect to the Binance API using our public and secret keys.
        try:
            self.client = Client('lfeDDamF6ckP7A2uWrd7uJ5nV0aJedQwD2H0HGujNuxmGgtyQQt0kL3lS6UFlRLS', 'phpomS4lCMKuIxF0BgrP4d5N9rEPzf8Dy4ZRVjJ0XeO4Wn7PmOC7uhYsyypi9gFJ')
        except:
            utilities.throw_error('Failed to Connect to Binance API', True)
        utilities.throw_info('Successfully Connected to Binance Client')

        # TODO: Set this to utilities.COINPAIRS when no longer testing.
        self.coinpairs = ['ICXBTC']

        # Acquire all necessary historical data from the API for each coinpair.
        try:
            self.data = {}
            for coinpair in self.coinpairs:

                # Instantiate a new Coinpair object for this coinpair.
                self.data[coinpair] = Coinpair(coinpair)

                # Query the API for the latest 1000 entry points.
                tempData = pandas.DataFrame(self.client.get_klines(symbol=coinpair, interval=Client.KLINE_INTERVAL_1MINUTE), columns=utilities.COLUMN_STRUCTURE)

                # Create a Candle and add it to the Coinpair for each entry returned by the API.
                for index, candle in tempData.iterrows():
                    self.data[coinpair].add_candle(Candle(candle['Open Time'], candle['Open'], candle['High'], candle['Low'], candle['Close'], candle['Close Time']), False)

                # Remove the last one as that's the current (incomplete) kline.
                self.data[coinpair].data = self.data[coinpair].data[:-1]

                # Update the overhead information for this Coinpair.
                self.data[coinpair].update_overhead()

                # Add the specific information associated with this coinpair.
                self.data[coinpair].add_info(self.client.get_symbol_info(coinpair))
        except:
            utilities.throw_error('Failed to Get Historical Data', True)
        utilities.throw_info('Successfully Finished Getting Historical Data')

        # Create the websocket manager and all necessary connections.
        try:
            self.sockets = Sockets(self)
        except:
            utilities.throw_error('Failed to Start Socket Manager', True)
        utilities.throw_info('Successfully Completed WebSocket Connections')

        # This holds all positions, open or closed, that this bot has created.
        self.positions = []

        # Import saved positions from previous bot usages.
        try:
            with open('positions.csv', newline='\n') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    position = Position(row[1], row[3], row[5], row[6], row[7])
                    position.open = row[0]
                    position.sellId = row[2]
                    position.age = row[4]
                    position.current = row[8]
                    position.fee = row[9]
                    position.result = row[10]
                    position.peak = row[11]
                    position.stopLoss = row[12]
                    self.positions.append(position)
        except:
            utilities.throw_error('Failed to Import Positions', True)
        utilities.throw_info('Successfully Imported Positions')

        # Import saved orders from previous bot usages.
        # This holds all open orders that the bot has created.
        # TODO: Do this.
        self.orders = []

        # This contains the available value for all assets being used.
        # This will be populated when self.update() runs.
        self.balances = {}

        # This contains the 20 most recent prices of each coinpair returned by the socket connection.
        self.recent = {}
        for coinpair in self.coinpairs:
            self.recent[coinpair] = []

        # Update all the recently imported information.
        self.update()

    # Use an order returned from Binance to create a new position for local tracking
    # This will only happen if an order is completely or partially filled
    # order - A returned order object from the API
    def create_position(self, order):
        self.positions.append(Position(order.orderId, order.transactTime, order.symbol, order.executedQty, order.price))

        # Notify the user of a new position.
        utilities.throw_info('New Position Added\n')

    # Update all open positions with the latest time and price of their coinpair.
    def update_positions(self):
        for position in self.positions:
            if not position.open: continue
            position.update(live.data[position.pair].data[-1].closeTime, live.data[position.pair].data[-1].close)

    # Export all positions in case we need to restart the bot.
    # This can also be used for external analysis.
    def export_positions(self):
        try:
            with open('positions.csv', 'w') as file:
                for position in self.positions:
                    file.write(position.toCSV() + '\n')
        except:
            utilities.throw_error('Failed to Export Positions', False)

    # Acquire the available value for all assets being used.
    def update_balances(self):
        try:
            for coinpair in self.coinpairs:

                self.balances[coinpair[:-3]] = Balance(self.client, coinpair[:-3])

            # Can't forget the base asset.
            self.balances['BTC'] = Balance(self.client, 'BTC')
        except:
            self.sockets.close_socket_manager()
            utilities.throw_error('Failed to Update Asset Balances', True)

    # Update the local orders information with our Binance account
    # New positions are created here if needed
    def update_orders(self):
        try:
            for order in self.orders:

                order.update()

                # Create a new position if the buy order has been filled.
                if order.status == 'FILLED' and order.side == 'BUY': self.create_position(order)

                # Update and close a position if the sell order has been filled.
                if order.status == 'FILLED' and order.side == 'SELL':
                    for position in self.positions:
                        if position.sellId == order.orderId:
                            position.update(order.transactTime, order.price)
                            position.open = False

                # Remove the order from our list if it was filled or cancelled. No new position needed.
                if order.status == 'FILLED' or order.status == 'CANCELED': self.orders.remove(order)

                # TODO: Handle orders that take too long and are never filled or are partially filled.
        except:
            self.sockets.close_socket_manager()
            utilities.throw_error('Failed to Update the Orders', True)

    # Export the orders in case we need to restart the bot.
    # TODO: Do this.
    def export_orders(self):
        return

    # Provide a simple function for triggering all framework related updates
    # This will also export the necessary information
    def update(self):
        self.update_positions()
        self.update_balances()
        self.update_orders()

        self.export_positions()
        self.export_orders()

    # Create a limit buy order on the provided coinpair at the provided price
    # coinpair - The coinpair we're buying with
    # price - The price at which we want to buy at
    def buy(self, coinpair, price):

        # Validate whether a valid buy order can be made and return the correct values to use.
        buyQuantity, buyPrice = self.data[coinpair].validate_buy(float(self.balances['BTC'].free) * 0.5, float(price))

        # Do not attempt a buy order if an invalid quantity was returned.
        if buyQuantity == '-1' or buyPrice == '-1': return False

        # Attempt a limit buy order.
        try:
            utilities.throw_info('Creating a Buy Order on ' + coinpair + ' at price ' + buyPrice + '\n')
            self.orders.append(Order(self.client, self.client.order_limit_buy(symbol=coinpair, quantity=buyQuantity, price=buyPrice)))
        except:
            utilities.throw_error('Failed to Create a Buy Order', False)
            return False

        return True

    # Create a sell order on the provided position
    # position - The position being sold
    # TODO: Do this.
    def sell(self, position):
        utilities.throw_info('Selling Position\n')

        position.open = False
