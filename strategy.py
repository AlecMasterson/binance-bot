import utilities


def check_buy(perm, coinpair, index):
    if index < 3: return
    if coinpair.overhead[index - 1]['macdDiff'] > 0: perm['aboveZero'] = True
    if index < utilities.WINDOW: return

    minimum = min([x['macdDiff'] for x in coinpair.overhead[index - utilities.WINDOW:index]])
    valid = False
    slowing = False

    # If the MACD Diff has gone above zero since the last trade.
    # If the MACD Diff is within utilities.PERCENT percent of the lowest MACD Diff in the historical window.
    if perm['aboveZero'] and coinpair.overhead[index - 1]['macdDiff'] < (minimum * utilities.PERCENT):
        if coinpair.overhead[index - 1]['macd'] < coinpair.overhead[index - 1]['macdSignal']:
            if coinpair.overhead[index - 1]['macdDiff'] > coinpair.overhead[index - 2]['macdDiff']: valid = True
            else: perm['goingDown'] += 1
            if coinpair.overhead[index - 3]['macdDiff'] - coinpair.overhead[index - 2]['macdDiff'] > coinpair.overhead[index - 2]['macdDiff'] - coinpair.overhead[index - 1]['macdDiff']: slowing = True

        # If the MACD Diff has descended more than twice below zero and is slowing down in it's descension.
        if perm['goingDown'] > 2 and slowing: valid = True

    if valid and coinpair.candles[index - 1].close < ((coinpair.overhead[index - 1]['upperband'] - coinpair.overhead[index - 1]['lowerband']) / 2) + coinpair.overhead[index - 1]['lowerband']:
        #bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        perm['goingDown'] = 0
        perm['aboveZero'] = False
        return coinpair.candles[index - 1].close

    return None


def check_sell(perm, coinpair, index):
    if index < 3: return
    if coinpair.overhead[index - 1]['macdDiff'] < 0: perm['belowZero'] = True
    if index < utilities.TOP_WINDOW: return

    maximum = max([x['macdDiff'] for x in coinpair.overhead[index - utilities.TOP_WINDOW:index]])
    valid = False
    slowing = False

    if perm['belowZero'] and coinpair.overhead[index - 1]['macdDiff'] > (maximum * utilities.TOP_PERCENT) and coinpair.overhead[index - 2]['macdDiff'] > coinpair.overhead[index - 3]['macdDiff']:
        if coinpair.overhead[index - 1]['macd'] > coinpair.overhead[index - 1]['macdSignal']:
            if coinpair.overhead[index - 1]['macdDiff'] < coinpair.overhead[index - 2]['macdDiff']: valid = True
            else: perm['goingUp'] += 1
            if coinpair.overhead[index - 2]['macdDiff'] - coinpair.overhead[index - 3]['macdDiff'] > coinpair.overhead[index - 1]['macdDiff'] - coinpair.overhead[index - 2]['macdDiff']: slowing = True

        if perm['goingUp'] > 2 and slowing: valid = True

    if valid and coinpair.candles[index - 1].close > ((coinpair.overhead[index - 1]['upperband'] - coinpair.overhead[index - 1]['lowerband']) / 2) + coinpair.overhead[index - 1]['lowerband']:
        #bot.plot_sell_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        perm['goingUp'] = 0
        perm['belowZero'] = False
        return True

    return False
