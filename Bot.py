import csv
import sys
import time
import argparse
import pandas

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


def to_datetime(time):
    return pandas.to_datetime(time, unit='ms')


def combined_total(data, balances):
    total = balances['BTC']
    for coinpair in utilities.COINPAIRS:
        total += data[coinpair].candles[-1].close * balances[coinpair[:-3]]
    return total


class Bot:

    def __init__(self, online=False, optimize=False):
        self.online = online
        self.optimize = optimize

        if self.online and self.optimize:
            utilities.throw_error('Cannot Be Online AND Optimizing...', True)

        if not self.optimize:
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
                self.data[coinpair] = Coinpair(self.client, coinpair, self.online)
        except:
            utilities.throw_error('Failed to Get Historical Data', True)
        utilities.throw_info('Successfully Finished Getting Historical Data')

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
            if self.online: self.balances[coinpair[:-3]] = Balance(self.client, coinpair[:-3])
            else: self.balances[coinpair[:-3]] = 0.0
        if self.online: self.balances['BTC'] = Balance(self.client, 'BTC')
        else: self.balances['BTC'] = 1.0

        self.recent = {}
        for coinpair in utilities.COINPAIRS:
            self.recent[coinpair] = []

        self.buy_triggers = [0.0] * utilities.NUM_TRIGGERS
        self.sell_triggers = [0.0] * utilities.NUM_TRIGGERS
        self.plot_triggers = []

    def reset(self):
        if not self.online:
            self.positions = []
            self.orders = []

            self.balances = {}
            for coinpair in utilities.COINPAIRS:
                self.balances[coinpair[:-3]] = 0.0
            self.balances['BTC'] = 1.0

            self.recent = {}
            for coinpair in utilities.COINPAIRS:
                self.recent[coinpair] = []

    def update_balances(self):
        if self.online:
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
                    if not self.online: self.balances[order.symbol[:-3]] += order.executedQty * 0.999
                    self.positions.append(Position(order.orderId, order.transactTime, order.symbol, order.executedQty, order.price))
                    self.orders.remove(order)
                    if self.online: utilities.throw_info('New Position Created for Coinpair ' + order.symbol)
                elif order.status == 'CANCELED':
                    self.orders.remove(order)
                    if not self.online: self.balances['BTC'] += order.used
                    if self.online: utilities.throw_info('Buy Order Cancelled for Coinpair ' + order.symbol)
            elif order.side == 'SELL':
                if order.status == 'FILLED':
                    if self.online: utilities.throw_info('Sell Order Filled')
                    for position in self.positions:
                        if position.sellId == order.orderId:
                            if not self.online: self.balances['BTC'] += order.executedQty * order.price * 0.999
                            position.update(order.transactTime, order.price)
                            position.open = False
                            self.orders.remove(order)
                            if self.online: utilities.throw_info('Position Closed for Coinpair ' + order.symbol + ' with Result: ' + str(position.result))
                elif order.status == 'CANCELED':
                    self.orders.remove(order)
                    for position in self.positions:
                        if position.sellId == order.orderId:
                            position.sellId = ''
                            if not self.online: self.balances[order.symbol[:-3]] += order.used
                            if self.online: utilities.throw_info('Sell Order Cancelled for Coinpair ' + order.symbol)

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
        buyQuantity, buyPrice, btcUsed = self.data[coinpair].validate_order('BUY', self.balances['BTC'].free if self.online else self.balances['BTC'], price)
        if buyQuantity == -1 or buyPrice == -1: return False

        if self.online:
            try:
                self.orders.append(Order(self.client, self.client.order_limit_buy(symbol=coinpair, quantity=buyQuantity, price=buyPrice)))
            except:
                utilities.throw_error('Failed to Create a Buy Order', False)
        else:
            self.orders.append(
                Order(
                    None, {
                        'orderId': str(len(self.positions)) + '-BUY',
                        'symbol': coinpair,
                        'side': 'BUY',
                        'status': 'NEW',
                        'transactTime': self.recent[coinpair][-1].closeTime,
                        'price': buyPrice,
                        'origQty': buyQuantity,
                        'executedQty': buyQuantity
                    }, btcUsed))

            self.balances['BTC'] -= btcUsed

        if self.online: utilities.throw_info('Buy Order Created for Coinpair ' + coinpair + ' at Time: ' + str(to_datetime(self.recent[coinpair][-1]['time'])))

        self.update_balances()

        return True

    def sell(self, position):
        if position.sellId != '': return False

        sellQuantity, sellPrice, assetUsed = self.data[position.coinpair].validate_order('SELL', self.balances[position.coinpair[:-3]].free
                                                                                         if self.online else self.balances[position.coinpair[:-3]], position.current)
        if sellQuantity == -1 or sellPrice == -1: return False

        if self.online:
            try:
                order = Order(self.client, self.client.order_limit_sell(symbol=position.coinpair, quantity=sellQuantity, price=sellPrice))
                position.sellId = order.orderId
                self.orders.append(order)
            except:
                utilities.throw_error('Failed to Create a Sell Order', False)
        else:
            self.orders.append(
                Order(
                    None, {
                        'orderId': str(len(self.positions)) + '-SELL',
                        'symbol': position.coinpair,
                        'side': 'SELL',
                        'status': 'NEW',
                        'transactTime': self.recent[position.coinpair][-1].closeTime,
                        'price': sellPrice,
                        'origQty': sellQuantity,
                        'executedQty': sellQuantity
                    }, assetUsed))
            position.sellId = str(len(self.positions)) + '-SELL'
            self.balances[position.coinpair[:-3]] -= assetUsed

        if self.online: utilities.throw_info('Sell Order Created for Coinpair ' + position.coinpair + ' at Time: ' + str(to_datetime(self.recent[position.coinpair][-1]['time'])))

        self.update_balances()

        return True

    def plot(self, coinpair):
        plotData = [
            go.Candlestick(
                name='Candle Data',
                x=[to_datetime(candle.openTime) for candle in self.data[coinpair].candles],
                open=[candle.open for candle in self.data[coinpair].candles],
                high=[candle.high for candle in self.data[coinpair].candles],
                low=[candle.low for candle in self.data[coinpair].candles],
                close=[candle.close for candle in self.data[coinpair].candles],
                text=['MACD: ' + str(macd) for macd in self.data[coinpair].macd]),
            go.Scatter(name='Upper Bollinger Band', x=[to_datetime(candle.closeTime) for candle in self.data[coinpair].candles], y=[upperband for upperband in self.data[coinpair].upperband]),
            go.Scatter(name='Lower Bollinger Band', x=[to_datetime(candle.closeTime) for candle in self.data[coinpair].candles], y=[lowerband for lowerband in self.data[coinpair].lowerband]),
            go.Scatter(
                name='Bought',
                x=[to_datetime(position.time) for position in self.positions],
                y=[position.price for position in self.positions],
                mode='markers',
                marker=dict(size=12, color='orange'),
                text=[position.price for position in self.positions]),
            go.Scatter(
                name='Sold',
                x=[to_datetime(position.time + position.age) for position in self.positions],
                y=[position.price * position.result for position in self.positions],
                mode='markers',
                marker=dict(size=12, color='blue'),
                text=[position.price for position in self.positions]),
            go.Scatter(
                name='Triggers', x=[to_datetime(point['time']) for point in self.plot_triggers], y=[point['price'] for point in self.plot_triggers], mode='markers', marker=dict(size=9, color='red'))
        ]
        layout = go.Layout(showlegend=False, xaxis=dict(rangeslider=dict(visible=False)))
        py.plot(go.Figure(data=plotData, layout=layout), filename='plot.html')

    def run_backtest(self, coinpair):
        for index, candle in enumerate(self.data[coinpair].candles):
            if index == 0: continue

            self.recent[coinpair].append(self.data[coinpair].candles[index - 1])
            self.update()

            for position in self.positions:
                if position.open: strategy.check_sell(self, position, index)

            strategy.check_buy(self, coinpair, index)

        total = combined_total(self.data, self.balances)
        if self.optimize: self.reset()

        return total

    def print_optimize(self):
        print(utilities.ORDER_TIME_LIMIT, utilities.STOP_LOSS_ARM, utilities.STOP_LOSS)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='An Automated Binance Exchange Trading Bot')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-o', '--online', help='run the Bot live on the exchange', action='store_true')
    group.add_argument('-p', '--plot', help='plot results using Plotly', action='store_true')
    args = parser.parse_args()

    if not args.online:
        # TODO: Support backtesting across multiple coinpairs
        coinpair = utilities.COINPAIRS[0]
        bot = Bot()

        total = bot.run_backtest(coinpair)

        utilities.throw_info('Open Orders: ' + str(len(bot.orders)))
        utilities.throw_info('Total Balance: ' + str(total))

        if args.plot: bot.plot(coinpair)

    # TODO: Complete and test...
    else:
        bot = Bot(True)

        while True:
            bot.update()

            time.sleep(30)
