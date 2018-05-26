class Order:

    # Initialize a new Order with the required information
    def __init__(self, client, used, order):
        self.client = client

        self.used = used
        self.orderId = order['orderId']
        self.symbol = order['symbol']
        self.side = order['side']
        self.status = order['status']
        self.transactTime = order['transactTime']
        self.price = order['price']
        self.origQty = order['origQty']
        self.executedQty = order['executedQty']

    # Update the order using the latest information
    # NOTE: This has an API call
    def update(self):

        # Get the order information using the unique self.orderId value.
        updated = self.client.get_order(symbol=self.symbol, orderId=self.orderId)

        # These are the only three values that we want to update.
        self.executedQty = updated['executedQty']
        self.status = updated['status']
        self.time = updated['time']