import utilities, pandas


def to_datetime(time):
    return pandas.to_datetime(time, unit='ms')


class Position:

    # Initialize a new Position with the required information
    # Add additional default values for other variables
    def __init__(self, buyId, time, coinpair, amount, price):
        self.open = True
        self.buyId = buyId
        self.sellId = ''
        self.time = time
        self.age = 0
        self.coinpair = coinpair
        self.amount = amount
        self.price = price
        self.current = price
        self.fee = 0.0
        self.result = 0.0
        self.peak = 0.0
        self.stopLoss = False

    # Update the percent gain/loss of this Position and the highest % reached
    # Mark self.stopLoss if threshold is met
    # TODO: Include the fee in the calculation
    def update_result(self):
        self.result = self.current / self.price

        # Update the peak if needed.
        if self.result > self.peak: self.peak = self.result

        # Trigger a stopLoss if the peak threshold was reached and we have since fallen a certain amount.
        if self.peak > utilities.STOP_LOSS_ARM and self.peak - self.result > utilities.STOP_LOSS: self.stopLoss = True

    # Update the age and current price of the Position, then update the result
    # time - New time, in milliseconds, associated with the Position
    # price - New price associated with the Position
    def update(self, time, price):
        self.age = time - self.time
        self.current = price
        self.update_result()

    # Return a String interpretation of the Position for visualizing
    # Only include necessary information
    def toString(self):
        return 'Open: ' + str(self.open) + '\tTime: ' + str(to_datetime(self.time)) + '\tCoinPair: ' + str(self.coinpair) + '\tResult: ' + str(self.result)

    # Return all data regarding the Position as a comma separated String for exporting
    def toCSV(self):
        return str(self.open) + ',' + str(self.buyId) + ',' + str(self.sellId) + ',' + str(self.time) + ',' + str(self.age) + ',' + str(self.coinpair) + ',' + str(self.amount) + ',' + str(
            self.price) + ',' + str(self.current) + ',' + str(self.fee) + ',' + str(self.result) + ',' + str(self.peak) + ',' + str(self.stopLoss)
