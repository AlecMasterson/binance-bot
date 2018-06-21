import utilities


class Order:

    def __init__(self, client, order):
        self.client = client
        self.orderId = str(order['orderId'])
        self.symbol = str(order['symbol'])
        self.side = str(order['side'])
        self.status = str(order['status'])
        self.transactTime = int(order['transactTime'])
        self.price = float(order['price'])
        self.origQty = float(order['origQty'])
        self.executedQty = float(order['executedQty'])

    def update(self):
        try:
            updated = self.client.get_order(symbol=self.symbol, orderId=self.orderId)

            self.executedQty = float(updated['executedQty'])
            self.status = float(updated['status'])
            self.time = int(updated['time'])
        except:
            utilities.throw_error('Failed to Update Order', False)
