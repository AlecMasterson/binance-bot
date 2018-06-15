import utilities


def slope(x1, x2, y1, y2):
    return (y2 - y1) / (x2 - x1)


def check_buy(bot, curTime, candles, overhead):
    index = (curTime - utilities.START_DATE) / utilities.CANDLE_INTERVAL
    if index < 3: return

     if overhead.loc[curTime - utilities.CANDLE_INTERVAL]['macdDiff'] > 0: bot.aboveZero = True

    if index < utilities.WINDOW: return

    # TODO: DO THIS LINE.
    minimum = min(bot.data[coinpair].macdDiff[index - utilities.WINDOW:index])

    valid = False

    macdSlope = slope(1, 2, bot.data[coinpair].macd[index - 2], bot.data[coinpair].macd[index - 1])
    signalSlope = slope(1, 2, bot.data[coinpair].macdSignal[index - 2], bot.data[coinpair].macdSignal[index - 1])
    if bot.aboveZero and bot.data[coinpair].macdDiff[index - 1] < (minimum * utilities.PERCENT) and bot.data[coinpair].macdDiff[index - 2] < bot.data[coinpair].macdDiff[index - 3]:
        if bot.data[coinpair].macd[index - 1] > bot.data[coinpair].macdSignal[index - 1]:
            if macdSlope > signalSlope: bot.slopes.append(macdSlope - signalSlope)
            else: valid = True
        elif bot.data[coinpair].macd[index - 1] < bot.data[coinpair].macdSignal[index - 1]:
            if macdSlope < signalSlope: bot.slopes.append(signalSlope - macdSlope)
            else: valid = True
        if len(bot.slopes) > 1 and bot.slopes[-1] - (bot.slopes[-2] - bot.slopes[-1]) < 0:
            valid = True

    if valid and bot.data[coinpair].candles[index - 1].close < ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]:
        bot.buy(coinpair, bot.recent[coinpair][-1].close)
        bot.plot_buy_triggers.append({'color': 'black', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.slopes = []
        bot.aboveZero = False


def check_sell(bot, position, index):
    coinpair = position.coinpair

    if bot.data[coinpair].macdDiff[index - 1] < 0: bot.belowZero = True

    if index < utilities.TOP_WINDOW: return
    maximum = max(bot.data[coinpair].macdDiff[index - utilities.TOP_WINDOW:index])

    macdSlope = slope(1, 2, bot.data[coinpair].macd[index - 2], bot.data[coinpair].macd[index - 1])
    signalSlope = slope(1, 2, bot.data[coinpair].macdSignal[index - 2], bot.data[coinpair].macdSignal[index - 1])

    valid = False

    if bot.belowZero and bot.data[coinpair].macdDiff[index - 1] > (maximum * utilities.TOP_PERCENT) and bot.data[coinpair].macdDiff[index - 2] > bot.data[coinpair].macdDiff[index - 3]:
        if bot.data[coinpair].macd[index - 1] > bot.data[coinpair].macdSignal[index - 1]:
            if macdSlope > signalSlope: bot.top_slopes.append(macdSlope - signalSlope)
            else: valid = True
        elif bot.data[coinpair].macd[index - 1] < bot.data[coinpair].macdSignal[index - 1]:
            if macdSlope < signalSlope: bot.top_slopes.append(signalSlope - macdSlope)
            else: valid = True
        if len(bot.top_slopes) > 1 and bot.top_slopes[-1] - (bot.top_slopes[-2] - bot.top_slopes[-1]) < 0:
            valid = True

    if valid and bot.data[coinpair].candles[index - 1].close > ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]:
        bot.sell(position)
        bot.plot_sell_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.top_slopes = []
        bot.belowZero = False

    return

    if position.stopLoss: bot.sell(position)
    elif position.result < utilities.DROP: bot.sell(position)
