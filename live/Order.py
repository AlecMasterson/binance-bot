class Order:

    # Initialize a new Order with the required information
    def __init__(self, client, order):
        self.client = client
        self.orderId = order['orderId']
        self.symbol = order['symbol']
        self.side = order['side']
        self.status = order['status']
        self.transactTime = order['transactTime']
        self.price = order['price']
        self.origQty = order['origQty']
        self.executedQty = order['executedQty']

    # Update the order using the API to get the latest information
    # NOTE: This has an API call
    def update(self):

        # Get the order information using the unique self.orderId value.
        updated = self.client.get_order(symbol=self.symbol, orderId=self.orderId)

        # These are the only three values that we want to update.
        self.executedQty = updated['executedQty']
        self.status = updated['status']
        self.time = updated['time']

    # Return all data regarding the position as a comma separated String for exporting
    def toCSV(self):
        return str(self.orderId) + ',' + str(self.symbol) + ',' + str(self.side) + ',' + str(self.status) + ',' + str(self.transactTime) + ',' + str(self.price) + ',' + str(self.origQty) + ',' + str(
            self.executedQty)
