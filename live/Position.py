import math


class Position:

    # Initialize a new Position with the required information
    # Add additional default values for other variables
    def __init__(self, buyId, time, coinpair, amount, price):
        self.open = 'True'
        self.buyId = buyId
        self.sellId = 'None'
        self.time = time
        self.age = 0
        self.coinpair = coinpair
        self.amount = amount
        self.price = price
        self.current = price
        self.fee = 0.0
        self.result = 0.0
        self.peak = 0.0
        self.stopLoss = 'False'

    # Update the percent gain/loss of this Position and the highest % reached
    # Mark self.stopLoss if threshold is met
    def update_result(self):
        self.result = str((float(self.current) - float(self.fee)) / float(self.price))

        # Update the peak if needed.
        if float(self.result) > float(self.peak): self.peak = self.result

        # NOTE: 1.01 means a 1% gain was reached. This value can be changed.
        if float(self.result) >= 1.01: self.stopLoss = 'True'

    # Update all attributes of the Position
    # time - New time, in milliseconds, associated with the Position
    # price - New price associated with the Position
    def update(self, time, price):
        self.age = str(float(time) - float(self.time))
        self.current = price

        # Handle our % gain/loss on the Position
        self.update_result()

    # Return a String interpretation of the Position for visualizing
    # Only include necessary information
    def toString(self):
        output = 'Open: ' + str(self.open) + '\t'
        output += 'Time: ' + str(self.time) + '\t'
        output += 'CoinPair: ' + str(self.coinpair) + '\t'
        output += 'Result: ' + str(self.result)
        return output

    # Return all data regarding the position as a comma separated String for exporting
    def toCSV(self):
        return str(self.open) + ',' + str(self.buyId) + ',' + str(self.sellId) + ',' + str(self.time) + ',' + str(self.age) + ',' + str(self.coinpair) + ',' + str(self.amount) + ',' + str(
            self.price) + ',' + str(self.current) + ',' + str(self.fee) + ',' + str(self.result) + ',' + str(self.peak) + ',' + str(self.stopLoss)
