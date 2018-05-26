from binance.client import Client

from components.Balance import Balance
from components.Coinpair import Coinpair
from components.Order import Order
from components.Position import Position
import utilities


class Offline:

    def __init__(self):

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

        self.balances = {'BTC': Balance(None, 'BTC', 1.0)}
        for coinpair in utilities.COINPAIRS:
            self.balances[coinpair[:-3]] = Balance(None, coinpair[:-3], 0.0)

        self.positions = []
        self.orders = []
        self.recent = None

    def create_position(self, order):
        self.positions.append(Position(order.orderId, order.transactTime, order.symbol, order.executedQty, order.price))

    def update_positions(self):
        for position in self.positions:
            if position.open and position.sellId == '' and self.recent != None:
                position.update(self.recent.closeTime, self.recent.close)

    def update_orders(self):
        for order in self.orders:
            if order.price < self.recent.high and order.price > self.recent.low:
                if order.side == 'BUY':
                    self.balances[order.symbol[:-3]].free += order.executedQty
                    self.create_position(order)
                    self.orders.remove(order)
                    print('BOUGHT!\n\tBTC Balance: ' + str(self.balances['BTC'].free) + '\tAsset Balance: ' + str(self.balances[order.symbol[:-3]].free))
                elif order.side == 'SELL':
                    for position in self.positions:
                        if position.sellId == order.orderId:
                            position.update(order.transactTime, order.price)
                            position.open = False
                            self.balances['BTC'].free += order.executedQty * order.price
                            self.orders.remove(order)
                            print('SOLD!\n\tBTC Balance: ' + str(self.balances['BTC'].free) + '\tAsset Balance: ' + str(self.balances[order.symbol[:-3]].free))

            elif self.recent.closeTime - order.transactTime > utilities.ORDER_TIME_LIMIT:
                self.orders.remove(order)
                if order.side == 'SELL':
                    for position in self.positions:
                        if position.sellId == order.orderId:
                            position.sellId = ''
                            self.balances[order.symbol[:-3]].free += order.used
                elif order.side == 'BUY':
                    self.balances['BTC'].free += order.used
                print('CANCELLED! \n\tBTC Balance: ' + str(self.balances['BTC'].free) + '\tAsset Balance: ' + str(self.balances[order.symbol[:-3]].free))

    def update(self):
        self.update_orders()
        self.update_positions()

    def buy(self, coinpair, price):
        buyQuantity, buyPrice, btcUsed = self.data[coinpair].validate_order('BUY', self.balances['BTC'].free, price)
        if buyQuantity == -1 or buyPrice == -1: return False

        self.orders.append(
            Order(
                None, btcUsed, {
                    'orderId': str(len(self.positions)) + '-BUY',
                    'symbol': coinpair,
                    'side': 'BUY',
                    'status': None,
                    'transactTime': self.recent.closeTime,
                    'price': buyPrice,
                    'origQty': None,
                    'executedQty': buyQuantity
                }))

        self.balances['BTC'].free -= btcUsed

        return True

    def sell(self, position):
        if position.sellId != '': return False

        sellQuantity, sellPrice, assetUsed = self.data[position.coinpair].validate_order('SELL', self.balances[position.coinpair[:-3]].free, position.current)
        if sellQuantity == -1 or sellPrice == -1: return False

        self.orders.append(
            Order(
                None, assetUsed, {
                    'orderId': str(len(self.positions)) + '-SELL',
                    'symbol': position.coinpair,
                    'side': 'SELL',
                    'status': None,
                    'transactTime': self.recent.closeTime,
                    'price': sellPrice,
                    'origQty': None,
                    'executedQty': sellQuantity
                }))
        position.sellId = str(len(self.positions)) + '-SELL'

        self.balances[position.coinpair[:-3]].free -= assetUsed

        return True
