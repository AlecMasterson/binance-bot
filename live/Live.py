from binance.client import Client

import time, datetime, pandas, csv
import utilities

from Coinpair import Coinpair
from Candle import Candle
from Sockets import Sockets
from Position import Position
from Balance import Balance
from Order import Order


class Live:

    # Initialize a new Live object, which is the framework to the live bot
    # TODO: Set self.coinpairs to utilities.COINPAIRS when no longer testing.
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
        except FileNotFoundError:
            utilities.throw_info('No Positions to Import')
        except:
            utilities.throw_error('Failed to Import Positions', True)
        utilities.throw_info('Successfully Imported Positions')

        # This holds all open orders that the bot has created.
        self.orders = []

        # Import saved orders from previous bot usages.
        try:
            with open('orders.csv', newline='\n') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    order = {}
                    order['orderId'] = row[0]
                    order['symbol'] = row[1]
                    order['side'] = row[2]
                    order['status'] = row[3]
                    order['transactTime'] = row[4]
                    order['price'] = row[5]
                    order['origQty'] = row[6]
                    order['executedQty'] = row[7]
                    self.orders.append(Order(self.client, order))
        except FileNotFoundError:
            utilities.throw_info('No Orders to Import')
        except:
            utilities.throw_error('Failed to Import Orders', True)
        utilities.throw_info('Successfully Imported Orders')

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
            if position.open == 'False' or len(self.recent[position.coinpair]) < 1: continue
            position.update(self.recent[position.coinpair][-1]['time'], self.recent[position.coinpair][-1]['price'])

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
    # TODO: Handle SELL orders that take too long AND are partially filled.
    def update_orders(self):
        try:
            for order in self.orders:

                order.update()

                # Create a new position if the buy order has been filled or is taking too long.
                # If it took too long to fill, make sure it was at least partially filled.
                if order.side == 'BUY' and (order.status == 'FILLED' or (float(order.executedQty) != 0.0 and float(order.time) - float(order.transactTime) >= 3e5)):
                    self.create_position(order)
                    self.orders.remove(order)

                # Update and close a position if the sell order has been filled or is taking too long.
                # If it took too long to fill, make sure it was at least partially filled.
                elif order.side == 'SELL' and (order.status == 'FILLED' or (float(order.executedQty) != 0.0 and float(order.time) - float(order.transactTime) >= 3e5)):
                    for position in self.positions:

                        # Make sure we are editting the correct position.
                        if position.sellId == order.orderId:

                            # Update the position with the information returned from the order.
                            position.update(order.transactTime, order.price)

                            position.open = 'False'
                            utilities.throw_info('Position Closed\n')

                            self.orders.remove(order)

                # Remove the order from our list if it was cancelled or took too long without being partially filled.
                if order.status == 'CANCELED' or (float(order.executedQty) == 0.0 and float(order.time) - float(order.transactTime) >= 3e5):
                    self.orders.remove(order)

                    # Reset the sellId of the position if it were a sell order.
                    if order.side == 'SELL':
                        for position in self.positions:
                            if position.sellId == order.orderId: position.sellId = 'None'

        except:
            self.sockets.close_socket_manager()
            utilities.throw_error('Failed to Update the Orders', True)

    # Export the orders in case we need to restart the bot.
    def export_orders(self):
        try:
            with open('orders.csv', 'w') as file:
                for order in self.orders:
                    file.write(order.toCSV() + '\n')
        except:
            utilities.throw_error('Failed to Export Orders', False)

    # Provide a simple function for triggering all framework related updates
    # This will also export the necessary information
    def update(self):
        self.update_orders()
        self.update_balances()
        self.update_positions()

        self.export_positions()
        self.export_orders()

        # Output the current status to the user after updating everything.
        self.current_status('New Iteration at Time: ' + str(datetime.datetime.now()))

    # Output to the user the current status of everything in the Live framework
    # header - The starting text to the output
    def current_status(self, header):

        # Build the continuous output string starting with the header.
        output = header

        # Add the current BTC account balance.
        output += '\n\tBalances:\n\t\tBTC: ' + str(self.balances['BTC'].free)

        # Add on the remaining asset balances.
        for coinpair in self.coinpairs:
            output += '\n\t\t' + coinpair[:-3] + ': ' + str(self.balances[coinpair[:-3]].free)

        output += '\n\tOpen Orders: ' + str(len(self.orders))

        # Output how many open positions there are and what they are.
        open = 0
        tempOutput = ''
        for position in self.positions:
            if position.open == 'True':
                open += 1
                tempOutput += '\n\t\tTime: ' + str(position.time) + '\tResult: ' + str(position.result)
        output += '\n\tCurrent Open Positions: ' + str(open) + tempOutput + '\n'

        # Log this information.
        utilities.throw_info(output)

    # Create a limit buy order on the provided coinpair at the provided price
    # coinpair - The coinpair we're buying with
    # price - The price at which we want to buy at
    def buy(self, coinpair, price):

        # Validate whether a valid buy order can be made and return the correct values to use.
        buyQuantity, buyPrice = self.data[coinpair].validate_order('buy', float(self.balances['BTC'].free), float(price))

        # Do not attempt a buy order if an invalid quantity was returned.
        if buyQuantity == '-1' or buyPrice == '-1': return False

        # Attempt a limit buy order.
        try:
            utilities.throw_info('Creating a Buy Order on ' + coinpair + ' for ' + str(buyQuantity) + ' quantity at price ' + buyPrice + '\n')
            self.orders.append(Order(self.client, self.client.order_limit_buy(symbol=coinpair, quantity=buyQuantity, price=buyPrice)))
        except:
            utilities.throw_error('Failed to Create a Buy Order', False)
            return False

        # Update the balances after making this order.
        self.update_balances()

        return True

    # Create a sell order on the provided position
    # position - The position being sold
    def sell(self, position):

        # Don't sell a position twice.
        if position.sellId != 'None': return False

        # Validate whether a valid sell order can be made and return the correct values to use.
        sellQuantity, sellPrice = self.data[position.coinpair].validate_order('sell', float(self.balances[position.coinpair[:-3]].free), float(position.current))

        # Do not attempt a sell order if an invalid quantity was returned.
        if sellQuantity == '-1' or sellPrice == '-1': return False

        # Attempt a limit sell order.
        try:
            utilities.throw_info('Creating a Sell Order on ' + position.coinpair + ' for ' + str(sellQuantity) + ' quantity at price ' + sellPrice + '\n')
            order = Order(self.client, self.client.order_limit_sell(symbol=position.coinpair, quantity=sellQuantity, price=sellPrice))

            # Update the necessary information.
            position.sellId = order.orderId
            self.orders.append(order)
        except:
            utilities.throw_error('Failed to Create a Sell Order', False)
            return False

        # Update the balances after making this order.
        self.update_balances()

        return True
