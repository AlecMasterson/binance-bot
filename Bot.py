import csv
import sys
import time
import argparse
import pandas
import datetime
import os

from binance.client import Client

import strategy
import utilities
from components.Balance import Balance
from components.Coinpair import Coinpair
from components.Order import Order
from components.Position import Position
from components.Sockets import Sockets
import traceback


def combined_total(data, balances):
    total = balances['BTC'].free
    for coinpair in utilities.COINPAIRS:
        total += data[coinpair].candles[-1].close * balances[coinpair[:-3]].free
    return total


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
                utilities.throw_info('Importing Historical Data and Info for ' + coinpair + '...')
                self.data[coinpair] = Coinpair(self.client, coinpair)
        except:
            utilities.throw_error('Failed to Import Historical Data and Info', True)
        utilities.throw_info('Successfully Finished Importing All Historical Data and Info')

        if self.online:
            try:
                self.sockets = Sockets(self)
            except:
                self.sockets.close_socket_manager()
                utilities.throw_error('Failed to Start Socket Manager', True)
            utilities.throw_info('Successfully Finished Starting the Socket Manager')

            self.positions = []
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

        self.perm = {'aboveZero': False, 'belowZero': False, 'slopes': [], 'top_slopes': []}

    # ONLINE ONLY
    def update_balances(self):
        if not self.online: return

        for balance in self.balances:
            balance.update()

    # ONLINE ONLY
    def update_orders(self):
        if not self.online: return

        for order in self.orders:
            # TODO: Check if the order time is changed with every online update.

            order.update()
            if order.status != 'FILLED' and self.recent[order.symbol][-1]['time'] - order.transactTime > utilities.ORDER_TIME_LIMIT * 3e5:
                try:
                    self.client.cancel_order(symbol=order.symbol, orderId=order.orderId)
                except:
                    utilities.throw_error('Failed to Cancel Order', False)

            if order.side == 'BUY':
                if order.status == 'FILLED':
                    utilities.throw_info('Buy Order Filled')
                    self.positions.append(Position(order.orderId, order.transactTime, order.symbol, order.executedQty, order.price))
                    self.orders.remove(order)
                    utilities.throw_info('New Position Created for Coinpair ' + order.symbol)
                elif order.status == 'CANCELED':
                    self.orders.remove(order)
                    utilities.throw_info('Buy Order Cancelled for Coinpair ' + order.symbol)
            elif order.side == 'SELL':
                if order.status == 'FILLED':
                    utilities.throw_info('Sell Order Filled')
                    for position in self.positions:
                        if position.sellId == order.orderId:
                            position.update(order.transactTime, order.price)
                            position.open = False
                            self.orders.remove(order)
                            utilities.throw_info('Position Closed for Coinpair ' + order.symbol + ' with Result: ' + str(position.result))
                elif order.status == 'CANCELED':
                    self.orders.remove(order)
                    for position in self.positions:
                        if position.sellId == order.orderId:
                            position.sellId = ''
                            utilities.throw_info('Sell Order Cancelled for Coinpair ' + order.symbol)

    # ONLINE ONLY
    def update_positions(self):
        if not self.online: return

        for position in self.positions:
            if position.open and position.sellId == '' and len(self.recent[position.coinpair]) > 0:
                position.update(self.recent[position.coinpair][-1]['time'], self.recent[position.coinpair][-1]['price'])

    # ONLINE ONLY
    def update(self):
        if not self.online: return

        self.update_balances()
        self.update_orders()
        self.update_positions()
        self.update_balances()

        self.export_data()

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

    # ONLINE ONLY
    def buy(self, coinpair, price):
        if not self.online: return

        buyQuantity, buyPrice, btcUsed = coinpair.validate_order('BUY', self.balances['BTC'].free, price)
        if buyQuantity == -1 or buyPrice == -1: return False

        try:
            self.orders.append(Order(self.client, self.client.order_limit_buy(symbol=coinpair.coinpair, quantity=buyQuantity, price=buyPrice)))
            utilities.throw_info('Buy Order Created for Coinpair ' + coinpair + ' at Time: ' + str(utilities.to_datetime(self.recent[coinpair][-1]['time'])))
        except:
            utilities.throw_error('Failed to Create a Buy Order', False)

        return True

    # ONLINE ONLY
    def sell(self, position, coinpair):
        if not self.online or position.sellId != '': return False

        sellQuantity, sellPrice, assetUsed = coinpair.validate_order('SELL', self.balances[coinpair.coinpair[:-3]].free, position.current)
        if sellQuantity == -1 or sellPrice == -1: return False

        try:
            order = Order(self.client, self.client.order_limit_sell(symbol=coinpair.coinpair, quantity=sellQuantity, price=sellPrice))
            position.sellId = order.orderId
            self.orders.append(order)
            utilities.throw_info('Sell Order Created for Coinpair ' + position.coinpair + ' at Time: ' + str(utilities.to_datetime(self.recent[position.coinpair][-1]['time'])))
        except:
            utilities.throw_error('Failed to Create a Sell Order', False)

        self.update_balances(None if self.online else coinpair.coinpair[:-3], None if self.online else (-1 * assetUsed))
        return True

    def check_time_limit(self, coinpair, price, index):
        startTime = coinpair.candles[index].closeTime
        curIndex = index
        while curIndex < len(coinpair.candles) and coinpair.candles[curIndex].closeTime - startTime <= utilities.ORDER_TIME_LIMIT * 3e5:
            if price < coinpair.candles[curIndex].high and price > coinpair.candles[curIndex].low: return True
            curIndex += 1
        return False

    def prev_position(self, positions, index, coinpair):
        curIndex = index - 1
        while curIndex >= 0:
            if positions[curIndex].coinpair == coinpair: return curIndex
            curIndex -= 1
        return None

    def run_backtest(self):
        trade_points = {}
        combinedPositions = []

        for coinpair in utilities.COINPAIRS:
            trade_points[coinpair] = {'buy': [], 'positions': [], 'sell': []}
            utilities.throw_info('Simulating Coinpair ' + coinpair + '...')

            for index, candle in enumerate(self.data[coinpair].candles):
                if index == 0: continue

                price = strategy.check_buy(self.perm, self.data[coinpair], index)
                if price != None and self.check_time_limit(self.data[coinpair], price, index):
                    trade_points[coinpair]['buy'].append({'index': index - 1, 'time': self.data[coinpair].candles[index - 1].closeTime})
                    trade_points[coinpair]['positions'].append(Position(None, self.data[coinpair].candles[index - 1].closeTime, coinpair, None, price))

                for position in trade_points[coinpair]['positions']:
                    if not position.open: continue

                    position.update(self.data[coinpair].candles[index - 1].closeTime, self.data[coinpair].candles[index - 1].close)

                    if strategy.check_sell(position, self.perm, self.data[coinpair], index) and self.check_time_limit(self.data[coinpair], position.current, index):
                        trade_points[coinpair]['sell'].append({'index': index - 1, 'time': self.data[coinpair].candles[index - 1].closeTime})
                        position.open = False

            totalResult = 0.0
            count = 0
            finalPositions = []
            otherPositions = []
            for index, position in enumerate(trade_points[coinpair]['positions']):
                combinedPositions.append(position)

                if index < 2: continue
                if trade_points[coinpair]['positions'][index - 1].result > 1.0 and trade_points[coinpair]['positions'][index - 2].result > 1.0 and (
                        len(finalPositions) == 0 or position.time > finalPositions[-1].time + finalPositions[-1].age):
                    if totalResult != 0.0: totalResult *= position.result
                    else: totalResult = position.result
                    count += 1
                    finalPositions.append(position)
                else:
                    otherPositions.append(position)
            utilities.throw_info('Successfully Simulated ' + coinpair + ' with Resulting ' + str(totalResult * 100) + ' % ROI over ' + str(count) + ' Positions')

            utilities.throw_info('Exporting Results from Coinpair ' + coinpair + '...')
            try:
                with open('data/backtesting/' + coinpair + '.csv', 'w') as file:
                    file.write('final,time,end,price,current\n')
                    for pos in finalPositions:
                        file.write('1,' + str(pos.time) + ',' + str(pos.time + pos.age) + ',' + str(pos.price) + ',' + str(pos.current) + '\n')
                    for pos in otherPositions:
                        file.write('0,' + str(pos.time) + ',' + str(pos.time + pos.age) + ',' + str(pos.price) + ',' + str(pos.current) + '\n')
            except:
                utilities.throw_error('Failed to Export Results from Coinpair ' + coinpair, False)
            utilities.throw_info('Successfully Exported Results from Coinpair ' + coinpair + '...')

        combinedPositions = sorted(combinedPositions, key=lambda k: k.time)

        # TODO: Finish below. Consider doing less than 100% each buy. Allow more than one position at a time.

        totalResult = 0.0
        count = 0
        finalPositions = []
        for index, position in enumerate(combinedPositions):
            if index < 2: continue
            prevPos = self.prev_position(combinedPositions, index, position.coinpair)
            if prevPos != None: prevPrevPos = self.prev_position(combinedPositions, prevPos, position.coinpair)
            else: prevPrevPos = None
            if (prevPos == None or combinedPositions[prevPos].result > 1.0) and (prevPrevPos == None or
                                                                                 combinedPositions[prevPrevPos].result > 1.0) and (len(finalPositions) == 0 or
                                                                                                                                   position.time > finalPositions[-1].time + finalPositions[-1].age):
                if totalResult != 0.0: totalResult *= position.result
                else: totalResult = position.result
                count += 1
                finalPositions.append(position)

        for pos in combinedPositions:
            print(pos.toString())

        print('\n\n\n\n')
        for pos in finalPositions:
            print(pos.toString())

        print(totalResult)

        #result = combined_total(self.data, self.balances)
        result = 0.0
        if self.optimize: self.reset()

        return result


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='An Automated Binance Exchange Trading Bot')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-o', '--online', help='run the Bot live on the exchange', action='store_true')
    group.add_argument('-p', '--plot', help='plot the following coinpairs after backtesting', nargs='+', type=str, action='append', dest='plotting')
    args = parser.parse_args()

    if not args.online:
        bot = Bot()

        utilities.throw_info('Starting Backtesting...')
        result = bot.run_backtest()
        utilities.throw_info('Successfully Completed Backtesting with Result: ' + str(result))

        if args.plotting != None:
            utilities.throw_info('Plotting Coinpairs ' + str(args.plotting[0]) + '...')
            for coinpair in args.plotting[0]:
                if not coinpair in utilities.COINPAIRS: utilities.throw_error('Coinpair \'' + coinpair + '\' Not Backtested', False)
                else: os.system('python plot.py -c ' + coinpair)
