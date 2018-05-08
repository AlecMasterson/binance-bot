import math


class Position:

    # Initialize a new Position with the required information
    # Add additional default values for other variables
    def __init__(self, buyId, time, pair, amount, price):
        self.open = True
        self.buyId = buyId
        self.sellId = None
        self.time = time
        self.age = 0
        self.pair = pair
        self.amount = amount
        self.price = price
        self.current = current
        self.fee = 0.0
        self.result = 0.0
        self.peak = 0.0
        self.stopLoss = False

    # Return True if the Position is currently being sold, False otherwise
    def selling(self):
        if self.open and self.sellId != None and not math.isnan(self.sellId): return True
        return False

    # Update the percent gain/loss of this Position and the highest % reached
    # Mark self.stopLoss if threshold is met
    def update_result(self):
        self.result = (self.current - self.fee) / self.price

        # Update the peak if needed.
        if self.result > self.peak: self.peak = self.result

        # NOTE: 1.01 means a 1% gain was reached. This value can be changed.
        if self.result >= 1.01: self.stopLoss = True

    # Update all attributes of the Position
    # time - New time, in milliseconds, associated with the Position
    # price - New price associated with the Position
    def update(self, time, price):
        self.age = time - self.time
        self.current = price

        # Handle our % gain/loss on the Position
        self.update_result()

    # Return a String interpretation of the Position
    # Only include necessary information
    def toString(self):
        output = 'Open: ' + str(self.open) + '\t'
        output += 'Time: ' + str(self.time) + '\t'
        output += 'CoinPair: ' + str(self.pair) + '\t'
        output += 'Result: ' + str(self.result)
        return output
