import utilities


def check_buy(perm, coinpair, index):
    if index < 3: return
    if coinpair.at[index - 1, 'MACD_DIFF'] > 0: perm['aboveZero'] = True
    if index < utilities.WINDOW: return

    minimum = min(coinpair[index - utilities.WINDOW:index]['MACD_DIFF'])
    valid = False
    slowing = False

    # If the MACD Diff has gone above zero since the last trade.
    # If the MACD Diff is within utilities.PERCENT percent of the lowest MACD Diff in the historical window.
    if perm['aboveZero'] and coinpair.at[index - 1, 'MACD_DIFF'] < (minimum * utilities.PERCENT):
        if coinpair.at[index - 1, 'MACD'] < coinpair.at[index - 1, 'MACD_SIGNAL']:
            if coinpair.at[index - 1, 'MACD_DIFF'] > coinpair.at[index - 2, 'MACD_DIFF']: valid = True
            else: perm['goingDown'] += 1
            if coinpair.at[index - 3, 'MACD_DIFF'] - coinpair.at[index - 2, 'MACD_DIFF'] > coinpair.at[index - 2, 'MACD_DIFF'] - coinpair.at[index - 1, 'MACD_DIFF']: slowing = True

        # If the MACD Diff has descended more than twice below zero and is slowing down in it's descension.
        if perm['goingDown'] > 2 and slowing: valid = True

    if valid and coinpair.at[index - 1, 'CLOSE'] < ((coinpair.at[index - 1, 'UPPERBAND'] - coinpair.at[index - 1, 'LOWERBAND']) / 2) + coinpair.at[index - 1, 'LOWERBAND']:
        #bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        perm['goingDown'] = 0
        perm['aboveZero'] = False
        return coinpair.at[index - 1, 'CLOSE']

    return None


def check_sell(perm, coinpair, index):
    if index < 3: return
    if coinpair.at[index - 1, 'MACD_DIFF'] < 0: perm['belowZero'] = True
    if index < utilities.TOP_WINDOW: return

    maximum = max(coinpair[index - utilities.WINDOW:index]['MACD_DIFF'])
    valid = False
    slowing = False

    if perm['belowZero'] and coinpair.at[index - 1, 'MACD_DIFF'] > (maximum * utilities.TOP_PERCENT) and coinpair.at[index - 2, 'MACD_DIFF'] > coinpair.at[index - 3, 'MACD_DIFF']:
        if coinpair.at[index - 1, 'MACD'] > coinpair.at[index - 1, 'MACD_SIGNAL']:
            if coinpair.at[index - 1, 'MACD_DIFF'] < coinpair.at[index - 2, 'MACD_DIFF']: valid = True
            else: perm['goingUp'] += 1
            if coinpair.at[index - 2, 'MACD_DIFF'] - coinpair.at[index - 3, 'MACD_DIFF'] > coinpair.at[index - 1, 'MACD_DIFF'] - coinpair.at[index - 2, 'MACD_DIFF']: slowing = True

        if perm['goingUp'] > 2 and slowing: valid = True

    if valid and coinpair.at[index - 1, 'CLOSE'] > ((coinpair.at[index - 1, 'UPPERBAND'] - coinpair.at[index - 1, 'LOWERBAND']) / 2) + coinpair.at[index - 1, 'LOWERBAND']:
        #bot.plot_sell_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        perm['goingUp'] = 0
        perm['belowZero'] = False
        return True

    return False
