import utilities


class Position:

    def __init__(self, buyId, time, coinpair, amount, price):
        self.open = True
        self.buyId = str(buyId)
        self.sellId = ''
        self.time = int(time)
        self.age = 0
        self.coinpair = str(coinpair)
        self.amount = float(amount)
        self.price = float(price)
        self.current = float(price)
        self.fee = 0.0
        self.result = 0.0
        self.peak = 0.0
        self.stopLoss = False

    # TODO: Include the fee in calculation.
    def update(self, time, price):
        self.age = time - self.time
        self.current = price
        self.result = self.current / self.price
        if self.result > self.peak: self.peak = self.result
        if self.peak > utilities.STOP_LOSS_ARM and self.peak - self.result > utilities.STOP_LOSS: self.stopLoss = True

    def toCSV(self):
        return str(self.open) + ',' + str(self.buyId) + ',' + str(self.sellId) + ',' + str(self.time) + ',' + str(self.age) + ',' + str(self.coinpair) + ',' + str(self.amount) + ',' + str(
            self.price) + ',' + str(self.current) + ',' + str(self.fee) + ',' + str(self.result) + ',' + str(self.peak) + ',' + str(self.stopLoss)

    def toString(self):
        return 'Coinpair: ' + self.coinpair + '\tOpen: ' + str(self.open) + '\tStart - End: ' + str(utilities.to_datetime(self.time)) + ' - ' + str(
            utilities.to_datetime(self.time + self.age)) + '\tResult: ' + str(self.result)
