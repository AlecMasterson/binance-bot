import utilities


class Order:

    # Initialize a new Order with the required information
    def __init__(self, client, order, used):
        self.client = client
        self.orderId = order['orderId']
        self.symbol = order['symbol']
        self.side = order['side']
        self.status = order['status']
        self.transactTime = int(order['transactTime'])
        self.price = float(order['price'])
        self.origQty = float(order['origQty'])
        self.executedQty = float(order['executedQty'])

        self.used = used

    # Update the Order using the latest information
    # NOTE: This has an API call
    def update(self):

        # Get the order information using the unique self.orderId value.
        try:
            updated = self.client.get_order(symbol=self.symbol, orderId=self.orderId)

            # These are the only three values that we want to update.
            self.executedQty = float(updated['executedQty'])
            self.status = float(updated['status'])
            self.time = int(updated['time'])
        except:
            utilities.throw_error('Failed to Update Order', False)
