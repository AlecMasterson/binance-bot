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

    # Update the order using the latest information
    # This chooses between online and offline mode
    # Parameters are required online for offline mode
    # executedQty - How much of the order has been filled
    # status - The current status of the order
    # time - The current time of the order
    def update(self, executedQty, status, time):
        if self.client != None: self.update_online()
        else self.update_offline(executedQty, status, time)

    # The online updating function
    # NOTE: This has an API call
    def update_online(self):

        # Get the order information using the unique self.orderId value.
        updated = self.client.get_order(symbol=self.symbol, orderId=self.orderId)

        # These are the only three values that we want to update.
        self.executedQty = updated['executedQty']
        self.status = updated['status']
        self.time = updated['time']

    # The offline updating function
    def update_offline(self, executedQty, status, time):
        self.executedQty = executedQty
        self.status = status
        self.time = time
