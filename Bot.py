from binance.client import Client
from components.Balance import Balance
from components.Coinpair import Coinpair
from components.Order import Order
from components.Position import Position
from components.Sockets import Sockets
import utilities, csv, pandas


# Convert a time from milliseconds to a pandas.DateTime object
# time - The time in milliseconds
def to_datetime(time):
    return pandas.to_datetime(time, unit='ms')


class Bot:

    def __init__(self, online):
        self.online = online

        try:
            self.client = Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
        except:
            utilities.throw_error('Failed to Connect to Binance API', True)
        utilities.throw_info('Successfully Finished Connecting to Binance Client')

        self.data = {}
        try:
            for coinpair in utilities.COINPAIRS:
                self.data[coinpair] = Coinpair(self.client, coinpair)
        except:
            utilities.throw_error('Failed to Get Historical Data', True)
        utilities.throw_info('Successfully Finished Getting Historical Data')

        if self.online:
            try:
                self.sockets = Sockets(self)
            except:
                utilities.throw_error('Failed to Start Socket Manager', True)
            utilities.throw_info('Successfully Finished Starting the Socket Manager')

        self.positions = []
        if self.online:
            try:
                with open('positions.csv', newline='\n') as file:
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
                utilities.throw_error('Failed to Import Positions', True)
            utilities.throw_info('Successfully Imported Positions')

        self.orders = []
        if self.online:
            try:
                with open('orders.csv', newline='\n') as file:
                    reader = csv.reader(file, delimiter=',')
                    for row in reader:
                        self.orders.append(Order(self.client, self.client.get_order(symbol=row[0], orderId=row[1])))
            except FileNotFoundError:
                utilities.throw_info('orders.csv FileNotFound... not importing Orders')
            except:
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
                if order.status != 'FILLED' and self.recent[order.symbol][-1]['time'] - order.transactTime > utilities.ORDER_TIME_LIMIT:
                    try:
                        self.client.cancel_order(symbol=order.symbol, orderId=order.orderId)
                    except:
                        utilities.throw_error('Failed to Cancel Order', False)
            elif order.price < self.recent[order.symbol][-1].high and order.price > self.recent[order.symbol][-1].low:
                order.status = 'FILLED'
            elif self.recent[order.symbol][-1].closeTime - order.transactTime > utilities.ORDER_TIME_LIMIT:
                order.status = 'CANCELED'

            if order.side == 'BUY':
                if order.status == 'FILLED':
                    if self.online: utilities.throw_info('Buy Order Filled')
                    if not self.online: self.balances[order.symbol[:-3]] += order.executedQty
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
                            if not self.online: self.balances['BTC'] += order.executedQty * order.price
                            position.update(order.transactTime, order.price)
                            position.open = False
                            self.orders.remove(order)
                            utilities.throw_info('Position Closed for Coinpair ' + order.symbol + ' with Result: ' + str(position.result))
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
            with open('positions.csv', 'w') as file:
                for position in self.positions:
                    file.write(position.toCSV() + '\n')
        except:
            utilities.throw_error('Failed to Export Positions', False)
        try:
            with open('orders.csv', 'w') as file:
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
