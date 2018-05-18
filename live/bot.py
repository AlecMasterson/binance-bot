import sys, time, datetime
import utilities

from Live import Live


# Determines if a specific time entry has already been marked as a potential buy order
# potentialFiltered - All potential buy orders of a given coinpair.
# time - The time, in milliseconds, we are checking for simularity.
def already_potential(potentialFiltered, time):

    # Loop through all the possible buy orders and return if the time was already found.
    exists = False
    for possible in potentialFiltered:
        if possible['time'] == time: exists = True

    return exists


# Search the 50 most recent prices returned from the socket connection for a low enough price
# prices - The 50 most recent prices
# time - It must be in the future relative to this time
# price - It must be less than or equal to this price
def price_found(prices, time, price):
    for finding in prices:
        if float(finding['time']) > time and float(finding['price']) <= price: return True
    return False


if __name__ == "__main__":

    # Instantiate the main framework for interacting with Binance.
    live = Live()

    # This contains potential positions if the price goes low enough.
    # This is my solution to having thousands of orders open, which isn't allowed on the exchange.
    potential = {}
    for coinpair in live.coinpairs:
        potential[coinpair] = []

    # Run the rest of the bot infinitely!
    while True:

        # Update the Live object every iteration.
        live.update()

        # Used for continuous updates to user.
        output = '\n'

        # Check each coinpair for a potential buy or sell trade.
        for coinpair in live.coinpairs:

            output += '\t' + coinpair + '\n'
            output += '\t\tMACD -2: ' + str(live.data[coinpair].macd[-2]) + '\tMACD -1: ' + str(live.data[coinpair].macd[-1]) + '\n\t\tBollinger: ' + str(
                live.data[coinpair].lowerband[-1]) + '\n\t\tPotential\n'
            for possible in potential[coinpair]:
                output += '\t\t\t' + str(possible['time']) + ':' + str(possible['price']) + '\n'
            output += '\n\t\tRecents\n'
            for recent in live.recent[coinpair][-7:]:
                output += '\t\t\t' + str(recent['time']) + ':' + str(recent['price']) + '\n'

            # Output to the user the built string of information.
            utilities.throw_info(output + '\n')

            # These MACD conditions determine if we should hold onto our position as the price is still rising.
            if live.data[coinpair].macd[-1] > live.data[coinpair].macd[-2] and live.data[coinpair].macd[-2] > 0: status = 'hold'
            else: status = ''

            # Analyze all the open positions of the current coinpair and test for a potential sell order.
            for position in live.positions:
                if position.open == 'True' and position.coinpair == coinpair:
                    if not status == 'hold' and position.stopLoss == 'True':
                        live.sell(position)
                    elif float(position.age) > 108e5 and float(position.result) < 0.99:
                        live.sell(position)

            # If the below MACD conditions are True, then we want to buy if the price reaches the most recent lowerband value.
            if not (live.data[coinpair].macd[-1] < live.data[coinpair].macd[-2]) and live.data[coinpair].macd[-2] < 0:

                # We don't want to mark a potential buy order more than once.
                if not already_potential(potential[coinpair], live.data[coinpair].data[-1].closeTime):

                    potential[coinpair].append({'used': False, 'coinpair': live.data[coinpair], 'time': live.data[coinpair].data[-1].closeTime, 'price': live.data[coinpair].lowerband[-1] * 0.99})
                    utilities.throw_info('New Potential at Price: ' + str(live.data[coinpair].lowerband[-1]) + '\n')

                # Check all potential buy orders of the current coinpair.
                for possible in potential[coinpair]:

                    if len(live.recent[coinpair]) < 1 or possible['used']: continue

                    # If it's been more than 18e5 milliseconds since the potential order was added, remove it.
                    # Else if the current price is low enough, buy!
                    if float(live.recent[coinpair][-1]['time']) - float(possible['time']) > 18e5:
                        potential[coinpair].remove(possible)
                    elif price_found(live.recent[coinpair], float(possible['time']), float(possible['price'])):

                        # Attempt to create a limit buy order through the API.
                        success = live.buy(coinpair, possible['price'])

                        # If the order was placed successfully, remove it.
                        if success: possible['used'] = True

        live.current_status('End of Iteration')

        # Stall the infinite loop for obvious reasons.
        time.sleep(30)
