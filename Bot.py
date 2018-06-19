import csv
import sys
import time
import argparse
import pandas
import datetime

import plotly.graph_objs as go
import plotly.offline as py
import plotly.tools as pytools
from binance.client import Client

import strategy
import utilities
from components.Balance import Balance
from components.Coinpair import Coinpair
from components.Order import Order
from components.Position import Position
from components.Sockets import Sockets
import traceback


def to_datetime(time):
    return pandas.to_datetime(time, unit='ms')


def combined_total(data, balances):
    total = balances['BTC'].free
    for coinpair in utilities.COINPAIRS:
        total += data[coinpair].candles[-1].close * balances[coinpair[:-3]].free
    return total


def get_time(position):
    return position.time


class Bot:

    def __init__(self, online=False, optimize=False):
        self.online = online
        self.optimize = optimize

        if self.online and self.optimize:
            utilities.throw_error('Cannot Be Online AND Optimizing', True)

        if self.online:
            try:
                self.client = Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
            except:
                utilities.throw_error('Failed to Connect to Binance API', True)
            utilities.throw_info('Successfully Finished Connecting to Binance Client')
        else:
            self.client = None

        self.data = {}
        try:
            for coinpair in utilities.COINPAIRS:
                utilities.throw_info('Importing History and Info for ' + coinpair + '...')
                self.data[coinpair] = Coinpair(self.client if self.online else None, coinpair)
        except:
            utilities.throw_error('Failed to Get Historical Data', True)
        utilities.throw_info('Successfully Finished Getting All Historical Data')

        if self.online:
            try:
                self.sockets = Sockets(self)
            except:
                self.sockets.close_socket_manager()
                utilities.throw_error('Failed to Start Socket Manager', True)
            utilities.throw_info('Successfully Finished Starting the Socket Manager')

        self.positions = []
        if self.online:
            try:
                with open('data/positions.csv', newline='\n') as file:
                    reader = csv.reader(file, delimiter=',')
                    for row in reader:
                        position = Position(row[1], int(row[3]), row[5], float(row[6]), float(row[7]))
                        position.open = True if row[0] == 'True' else False
                        position.sellId = row[2]
                        position.age = int(row[4])
                        position.current = float(row[8])
                        position.fee = float(row[9])
                        position.result = float(row[10])
                        position.peak = float(row[11])
                        position.stopLoss = True if row[12] == 'True' else False
                        self.positions.append(position)
            except FileNotFoundError:
                utilities.throw_info('positions.csv FileNotFound... not importing Positions')
            except:
                self.sockets.close_socket_manager()
                utilities.throw_error('Failed to Import Positions', True)
            utilities.throw_info('Successfully Imported Positions')

        self.orders = []
        if self.online:
            try:
                with open('data/orders.csv', newline='\n') as file:
                    reader = csv.reader(file, delimiter=',')
                    for row in reader:
                        self.orders.append(Order(self.client, self.client.get_order(symbol=row[0], orderId=row[1])))
            except FileNotFoundError:
                utilities.throw_info('orders.csv FileNotFound... not importing Orders')
            except:
                self.sockets.close_socket_manager()
                utilities.throw_error('Failed to Import Orders', True)
            utilities.throw_info('Successfully Imported Orders')

        self.balances = {}
        for coinpair in utilities.COINPAIRS:
            self.balances[coinpair[:-3]] = Balance(self.client, coinpair[:-3], None if self.online else 0.0)
        self.balances['BTC'] = Balance(self.client, 'BTC', None if self.online else 1.0)

        self.recent = {}
        for coinpair in utilities.COINPAIRS:
            self.recent[coinpair] = []

        self.plot_buy_triggers = []
        self.plot_sell_triggers = []

        self.perm = {'aboveZero': False, 'belowZero': False, 'slopes': [], 'top_slopes': []}

    # OFFLINE ONLY
    def reset(self):
        if self.online: return

        self.positions = []
        self.orders = []

        self.balances = {}
        for coinpair in utilities.COINPAIRS:
            self.balances[coinpair[:-3]] = Balance(self.client, coinpair[:-3], None if self.online else 0.0)
        self.balances['BTC'] = Balance(self.client, 'BTC', None if self.online else 1.0)

        self.recent = {}
        for coinpair in utilities.COINPAIRS:
            self.recent[coinpair] = []

        self.perm = {'aboveZero': False, 'belowZero': False, 'slopes': [], 'top_slopes': []}

    def update_balances(self, asset=None, amount=None):
        if not self.online and asset != None and amount != None:
            self.balances[asset].update(amount)
        elif self.online:
            for balance in self.balances:
                balance.update()

    def update_positions(self):
        for position in self.positions:
            if position.open and position.sellId == '' and len(self.recent[position.coinpair]) > 0:
                if self.online: position.update(self.recent[position.coinpair][-1]['time'], self.recent[position.coinpair][-1]['price'])
                else: position.update(self.recent[position.coinpair][-1].closeTime, self.recent[position.coinpair][-1].close)

    def update_orders(self):
        for order in self.orders:
            # TODO: Check if the order time is changed with every online update.
            if self.online:
                order.update()
                if order.status != 'FILLED' and self.recent[order.symbol][-1]['time'] - order.transactTime > utilities.ORDER_TIME_LIMIT * 3e5:
                    try:
                        self.client.cancel_order(symbol=order.symbol, orderId=order.orderId)
                    except:
                        utilities.throw_error('Failed to Cancel Order', False)
            elif order.price < self.recent[order.symbol][-1].high and order.price > self.recent[order.symbol][-1].low:
                order.status = 'FILLED'
            elif self.recent[order.symbol][-1].closeTime - order.transactTime > utilities.ORDER_TIME_LIMIT * 3e5:
                order.status = 'CANCELED'

            if order.side == 'BUY':
                if order.status == 'FILLED':
                    if self.online: utilities.throw_info('Buy Order Filled')
                    if not self.online: self.update_balances(order.symbol[:-3], order.executedQty * 0.999)
                    self.positions.append(Position(order.orderId, order.transactTime, order.symbol, order.executedQty, order.price))
                    self.orders.remove(order)
                    if self.online: utilities.throw_info('New Position Created for Coinpair ' + order.symbol)
                elif order.status == 'CANCELED':
                    self.orders.remove(order)
                    if not self.online: self.update_balances('BTC', order.used)
                    if self.online: utilities.throw_info('Buy Order Cancelled for Coinpair ' + order.symbol)
            elif order.side == 'SELL':
                if order.status == 'FILLED':
                    if self.online: utilities.throw_info('Sell Order Filled')
                    for position in self.positions:
                        if position.sellId == order.orderId:
                            if not self.online: self.update_balances('BTC', order.executedQty * order.price * 0.999)
                            position.update(order.transactTime, order.price)
                            position.open = False
                            self.orders.remove(order)
                            if self.online: utilities.throw_info('Position Closed for Coinpair ' + order.symbol + ' with Result: ' + str(position.result))
                elif order.status == 'CANCELED':
                    self.orders.remove(order)
                    for position in self.positions:
                        if position.sellId == order.orderId:
                            position.sellId = ''
                            if not self.online: self.update_balances(order.symbol[:-3], order.used)
                            if self.online: utilities.throw_info('Sell Order Cancelled for Coinpair ' + order.symbol)

    # ONLINE ONLY
    def export_data(self):
        if not self.online: return

        try:
            with open('data/positions.csv', 'w') as file:
                for position in self.positions:
                    file.write(position.toCSV() + '\n')
        except:
            utilities.throw_error('Failed to Export Positions', False)
        try:
            with open('data/orders.csv', 'w') as file:
                for order in self.orders:
                    file.write(order.symbol + ',' + order.orderId + '\n')
        except:
            utilities.throw_error('Failed to Export Orders', False)

    def update(self):
        self.update_balances()
        self.update_orders()
        self.update_positions()

        self.export_data()

    def buy(self, coinpair, price):
        buyQuantity, buyPrice, btcUsed = coinpair.validate_order('BUY', self.balances['BTC'].free, price)
        if buyQuantity == -1 or buyPrice == -1: return False

        if not self.online:
            self.orders.append(
                Order(
                    None, {
                        'orderId': str(len(self.positions)) + '-BUY',
                        'symbol': coinpair.coinpair,
                        'side': 'BUY',
                        'status': 'NEW',
                        'transactTime': self.recent[coinpair.coinpair][-1].closeTime,
                        'price': buyPrice,
                        'origQty': buyQuantity,
                        'executedQty': buyQuantity
                    }, btcUsed))
        else:
            try:
                self.orders.append(Order(self.client, self.client.order_limit_buy(symbol=coinpair.coinpair, quantity=buyQuantity, price=buyPrice)))
                utilities.throw_info('Buy Order Created for Coinpair ' + coinpair + ' at Time: ' + str(to_datetime(self.recent[coinpair][-1]['time'])))
            except:
                utilities.throw_error('Failed to Create a Buy Order', False)

        self.update_balances(None if self.online else 'BTC', None if self.online else (-1 * btcUsed))
        return True

    def sell(self, position, coinpair):
        if position.sellId != '': return False

        sellQuantity, sellPrice, assetUsed = coinpair.validate_order('SELL', self.balances[coinpair.coinpair[:-3]].free, position.current)
        if sellQuantity == -1 or sellPrice == -1: return False

        if not self.online:
            self.orders.append(
                Order(
                    None, {
                        'orderId': str(len(self.positions)) + '-SELL',
                        'symbol': coinpair.coinpair,
                        'side': 'SELL',
                        'status': 'NEW',
                        'transactTime': self.recent[coinpair.coinpair][-1].closeTime,
                        'price': sellPrice,
                        'origQty': sellQuantity,
                        'executedQty': sellQuantity
                    }, assetUsed))
            position.sellId = str(len(self.positions)) + '-SELL'
        else:
            try:
                order = Order(self.client, self.client.order_limit_sell(symbol=coinpair.coinpair, quantity=sellQuantity, price=sellPrice))
                position.sellId = order.orderId
                self.orders.append(order)
                utilities.throw_info('Sell Order Created for Coinpair ' + position.coinpair + ' at Time: ' + str(to_datetime(self.recent[position.coinpair][-1]['time'])))
            except:
                utilities.throw_error('Failed to Create a Sell Order', False)

        self.update_balances(None if self.online else coinpair.coinpair[:-3], None if self.online else (-1 * assetUsed))
        return True

    def run_backtest(self):
        final_positions = []
        for coinpair in utilities.COINPAIRS:
            for index, candle in enumerate(self.data[coinpair].candles):
                if index == 0: continue

                self.recent[coinpair].append(self.data[coinpair].candles[index - 1])
                self.update()

                for position in self.positions:
                    if position.open and strategy.check_sell(position, self.perm, self.data[coinpair], index): self.sell(position, self.data[position.coinpair])

                price = strategy.check_buy(self.perm, self.data[coinpair], index)
                if price != None: self.buy(self.data[coinpair], price)
            return combined_total(self.data, self.balances)
            utilities.throw_info('Backtesting ' + coinpair + ' Finished with ' + str(combined_total(self.data, self.balances)) + ' BTC')

            for position in self.positions:
                if not position.open: final_positions.append(position)
            self.reset()

        final_positions = sorted(final_positions, key=get_time)
        test = 0.0
        prevPos = None
        usedPos = []
        for position in final_positions:
            if prevPos == None:
                prevPos = position
                usedPos.append(position)
            elif position.time < prevPos.time + prevPos.age:
                continue
            if position.result > 1.0:
                test += position.result - 1.0
                prevPos = position
                usedPos.append(position)
        print(test)
        for pos in usedPos:
            print(pos.toString() + '\tEndTime: ' + str(to_datetime(pos.time + pos.age)))

        # -------------------------------------------------
        # EXPORT POSITION RESULTS FOR ANALYZING OR PLOTTING
        # -------------------------------------------------

        results = pandas.DataFrame(columns=['coinpair', 'startTime', 'endTime', 'startPrice', 'endPrice', 'result'])
        for position in self.positions:
            results = results.append(
                {
                    'coinpair': position.coinpair,
                    'startTime': position.time,
                    'endTime': position.time + position.age,
                    'startPrice': position.price,
                    'endPrice': position.current,
                    'result': position.result
                },
                ignore_index=True)
        results.to_csv('data/backtesting/results.csv', index=False)

        # ----------------------------
        # RETURN TOTAL ACCOUNT BALANCE
        # ----------------------------

        #result = combined_total(self.data, self.balances)
        result = 0.0
        if self.optimize: self.reset()

        return result


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='An Automated Binance Exchange Trading Bot')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-o', '--online', help='run the Bot live on the exchange', action='store_true')
    args = parser.parse_args()

    if not args.online:
        bot = Bot()

        utilities.throw_info('Starting Backtesting...')
        result = bot.run_backtest()
        utilities.throw_info('Successfully Completed Backtesting')

        # TODO: Cancel any open orders.

        utilities.throw_info('Open Orders: ' + str(len(bot.orders)))
        utilities.throw_info('Total Balance: ' + str(result))

    # TODO: Complete and test...
    else:
        sys.exit()
