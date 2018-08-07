import sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities


def action(data):
    #return action_trey(data)
    return action_alec(data)


# data - The most recent (utilities.WINDOW * 2) time entries
#        This is a pandas.DataFrame with columns utilities.HISTORY_STRUCTURE
def action_trey(data):
    # For you to implement your Agent code somehow.
    # Return Options: 'BUY', 'SELL', 'HOLD'
    return 'HOLD'


# This is my non-ML strategy to trade with. Read through it if you like, it's meh.
def action_alec(data):
    maximum = max(data[utilities.WINDOW:]['MACD_DIFF'])
    valid_sell = False

    if perm['belowZero'] and coinpair.at[index - 1, 'MACD_DIFF'] > (maximum * utilities.TOP_PERCENT) and coinpair.at[index - 2, 'MACD_DIFF'] > coinpair.at[index - 3, 'MACD_DIFF']:
        if coinpair.at[index - 1, 'MACD'] > coinpair.at[index - 1, 'MACD_SIGNAL']:
            if coinpair.at[index - 1, 'MACD_DIFF'] < coinpair.at[index - 2, 'MACD_DIFF']: valid = True
            else: perm['goingUp'] += 1
            if coinpair.at[index - 2, 'MACD_DIFF'] - coinpair.at[index - 3, 'MACD_DIFF'] > coinpair.at[index - 1, 'MACD_DIFF'] - coinpair.at[index - 2, 'MACD_DIFF']: slowing = True

        if perm['goingUp'] > 2 and slowing: valid = True

    # Only SELL if the MACD_DIFF is a certain percentage from the local maximum of the MACD_DIFF.
    if data.at[len(data) - 1, 'MACD_DIFF'] > (maximum * utilities.TOP_PERCENT):

        # I honestly forgot why I did this one.
        if data.at[len(data) - 2, 'MACD_DIFF'] > data.at[len(data) - 3, 'MACD_DIFF'] and data.at[len(data) - 1, 'MACD'] > data.at[len(data) - 1, 'MACD_SIGNAL']:

            # If the MACD_DIFF has started to fall, we can SELL.
            if data.at[len(data) - 1, 'MACD_DIFF'] < data.at[len(data) - 2, 'MACD_DIFF']: valid_sell = True

            # If the MACD_DIFF is slowing it's ascent and the last 3 were ascending.
            # For example: 4, 9, 11
            if data.at[len(data) - 2, 'MACD_DIFF'] - data.at[len(data) - 3, 'MACD_DIFF'] > data.at[len(data) - 1, 'MACD_DIFF'] - data.at[len(data) - 2, 'MACD_DIFF']:
                going_up = True
                for i in range(1, 4):
                    if data.at[len(data) - i, 'MACD_DIFF'] < data.at[len(data) - (i + 1), 'MACD_DIFF']: going_up = False
                if going_up: valid_sell = True

    # If the last CLOSE price was below the middle of the two Bollinger Bands, don't sell.
    if data.at[len(data) - 1, 'CLOSE'] <= ((data.at[len(data) - 1, 'UPPERBAND'] - data.at[len(data) - 1, 'LOWERBAND']) / 2) + data.at[len(data) - 1, 'LOWERBAND']:
        valid_sell = False
    if valid_sell: return 'SELL'

    minimum = min(data[utilities.WINDOW:]['MACD_DIFF'])
    valid_buy = False

    # Only BUY if the MACD_DIFF is a certain percentage from the local minimum of the MACD_DIFF.
    if data.at[len(data) - 1, 'MACD_DIFF'] < (minimum * utilities.PERCENT):

        # I honestly forgot why I did this one.
        if data.at[len(data) - 1, 'MACD'] < data.at[len(data) - 1, 'MACD_SIGNAL']:

            # If the MACD_DIFF has started to rise, we can BUY.
            if data.at[len(data) - 1, 'MACD_DIFF'] > data.at[len(data) - 2, 'MACD_DIFF']: valid_buy = True

            # If the MACD_DIFF is slowing it's descent and the last 3 were descending.
            # For example: -4, -9, -11
            if data.at[len(data) - 3, 'MACD_DIFF'] - data.at[len(data) - 2, 'MACD_DIFF'] > data.at[len(data) - 2, 'MACD_DIFF'] - data.at[len(data) - 1, 'MACD_DIFF']:
                going_down = True
                for i in range(1, 4):
                    if data.at[len(data) - i, 'MACD_DIFF'] > data.at[len(data) - (i + 1), 'MACD_DIFF']: going_down = False
                if going_down: valid_buy = True

    # If the last CLOSE price was above the middle of the two Bollinger Bands, don't buy.
    if data.at[len(data) - 1, 'CLOSE'] >= ((data.at[len(data) - 1, 'UPPERBAND'] - data.at[len(data) - 1, 'LOWERBAND']) / 2) + data.at[len(data) - 1, 'LOWERBAND']:
        valid_buy = False
    if valid_buy: return 'BUY'

    return 'HOLD'
