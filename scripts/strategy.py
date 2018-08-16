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


def get_value(data, past, column):
    return data.at[len(data) - 1 - past, column]


# This is my non-ML strategy to trade with. Read through it if you like, it's meh.
def action_alec(data, observation):
    if observation['selling']:
        if get_value(data, 0, 'MACD_DIFF') > get_value(data, 1, 'MACD_DIFF') and get_value(data, 1, 'MACD_DIFF') > get_value(data, 2, 'MACD_DIFF'):
            if get_value(data, 1, 'MACD_DIFF') - get_value(data, 2, 'MACD_DIFF') > get_value(data, 0, 'MACD_DIFF') - get_value(data, 1, 'MACD_DIFF'):
                return 'SELL', observation
    else:
        if get_value(data, 0, 'MACD_DIFF') < get_value(data, 1, 'MACD_DIFF') and get_value(data, 1, 'MACD_DIFF') < get_value(data, 2, 'MACD_DIFF'):
            if get_value(data, 2, 'MACD_DIFF') - get_value(data, 1, 'MACD_DIFF') > get_value(data, 1, 'MACD_DIFF') - get_value(data, 0, 'MACD_DIFF'):
                return 'BUY', observation
    return 'HOLD', observation

    if data[utilities.WINDOW:][-1:]['MACD_DIFF'].item() > observation['maximum']: observation['maximum'] = data[-1:]['MACD_DIFF'].item()
    if data[utilities.WINDOW:][-1:]['MACD_DIFF'].item() < observation['minimum']: observation['minimum'] = data[-1:]['MACD_DIFF'].item()
    if data[-1:]['MACD_DIFF'].item() > data[-2:-1]['MACD_DIFF'].item():
        observation['going_up'] += 1
        observation['going_down'] = 0
    elif data[-1:]['MACD_DIFF'].item() < data[-2:-1]['MACD_DIFF'].item():
        observation['going_up'] = 0
        observation['going_down'] += 1

    if observation['selling']:
        valid_sell = False

        # Only SELL if the MACD_DIFF is a certain percentage from the local maximum of the MACD_DIFF.
        if data[-1:]['MACD_DIFF'].item() > (observation['maximum'] * utilities.TOP_PERCENT):

            # I honestly forgot why I did this one.
            if data[-2:-1]['MACD_DIFF'].item() > data[-3:-2]['MACD_DIFF'].item() and data[-1:]['MACD'].item() > data[-1:]['MACD_SIGNAL'].item():

                # If the MACD_DIFF has started to fall, we can SELL.
                if data[-1:]['MACD_DIFF'].item() < data[-2:-1]['MACD_DIFF'].item(): valid_sell = True

                # If the MACD_DIFF is slowing it's ascent and the last 3 were ascending.
                # For example: 4, 9, 11
                if data[-2:-1]['MACD_DIFF'].item() - data[-3:-2]['MACD_DIFF'].item() > data[-1:]['MACD_DIFF'].item() - data[-2:-1]['MACD_DIFF'].item():
                    valid_sell = True

            # If the last CLOSE price was below the middle of the two Bollinger Bands, don't sell.
            if data[-1:]['CLOSE'].item() <= ((data[-1:]['UPPERBAND'].item() - data[-1:]['LOWERBAND'].item()) / 2) + data[-1:]['LOWERBAND'].item():
                valid_sell = False

            if valid_sell: return 'SELL', observation

    else:
        valid_buy = False

        # Only BUY if the MACD_DIFF is a certain percentage from the local minimum of the MACD_DIFF.
        if data[-1:]['MACD_DIFF'].item() < (observation['minimum'] * utilities.PERCENT):

            # I honestly forgot why I did this one.
            if data[-1:]['MACD'].item() < data[-1:]['MACD_SIGNAL'].item():

                # If the MACD_DIFF has started to rise, we can BUY.
                if data[-1:]['MACD_DIFF'].item() > data[-2:-1]['MACD_DIFF'].item(): valid_buy = True

                # If the MACD_DIFF is slowing it's descent and the last 3 were descending.
                # For example: -4, -9, -11
                if data[-3:-2]['MACD_DIFF'].item() - data[-2:-1]['MACD_DIFF'].item() > data[-2:-1]['MACD_DIFF'].item() - data[-1:]['MACD_DIFF'].item():
                    valid_buy = True

            # If the last CLOSE price was above the middle of the two Bollinger Bands, don't buy.
            if data[-1:]['CLOSE'].item() >= ((data[-1:]['UPPERBAND'].item() - data[-1:]['LOWERBAND'].item()) / 2) + data[-1:]['LOWERBAND'].item():
                valid_buy = False
            if valid_buy: return 'BUY', observation

    return 'HOLD', observation
