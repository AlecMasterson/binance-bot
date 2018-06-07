import utilities


# Returns True if num1 and num2 are with range % of each other
# num1 - The first number
# num2 - The second number
# range - Percent threshold to test
def within_range(num1, num2, range):
    if (num1 - num2) / num2 < range:
        return True
    return False


def check_buy(bot, coinpair, index):
    # Create a 3 hour buffer before allowing trading.
    if index < 36: return

    maxPrice = -1000.0
    maxPriceIndex = 0
    maxMACD = -1000.0
    minPrice = 1000.0
    minPriceIndex = 0
    minMACD = 1000.0
    minLower = 1000.0

    # Get the above values for the past 3 hours.
    for i in range(1, 37):
        if bot.data[coinpair].candles[index - i].close > maxPrice:
            maxPrice = bot.data[coinpair].candles[index - i].close
            maxPriceIndex = index - i
        if bot.data[coinpair].macd[index - i] > maxMACD:
            maxMACD = bot.data[coinpair].macd[index - i]
        if bot.data[coinpair].candles[index - i].close < minPrice:
            minPrice = bot.data[coinpair].candles[index - i].close
            minPriceIndex = index - i
        if bot.data[coinpair].macd[index - i] < minMACD:
            minMACD = bot.data[coinpair].macd[index - i]
        if bot.data[coinpair].lowerband[index - i] < minLower:
            minLower = bot.data[coinpair].lowerband[index - i]

    # Don't buy if price is trending up or if price is trending down and not slowling down.
    if bot.data[coinpair].macd[index - 1] > 0 or bot.data[coinpair].macd[index - 1] < bot.data[coinpair].macd[index - 2]: return
    # Don't buy if price is in the top half of the upper/lower BollingerBand range.
    if bot.data[coinpair].candles[index - 1].close >= ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]: return

    #if bot.data[coinpair].macd[index - 2] - bot.data[coinpair].macd[index - 1] > bot.data[coinpair].macd[index - 3] - bot.data[coinpair].macd[index - 2]: return

    #if bot.data[coinpair].lowerband[index - 2] == minLower and bot.data[coinpair].lowerband[index - 2] > bot.data[coinpair].lowerband[index - 1]: return

    if minPriceIndex > maxPriceIndex and maxPrice / bot.data[coinpair].candles[index - 1].close > 1.025:
        if bot.data[coinpair].candles[index - 1].close / minPrice > 1.005:
            bot.plot_buy_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        #bot.plot_buy_triggers.append({'color': 'green', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy_triggers[3] += utilities.TRIGGER_3
        #bot.buy(coinpair, bot.recent[coinpair][-1].close)
        return

    if bot.data[coinpair].candles[index - 1].close < bot.data[coinpair].lowerband[index - 1]:
        bot.plot_buy_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy_triggers[0] += utilities.TRIGGER_0
        #bot.buy(coinpair, bot.recent[coinpair][-1].close)
        return
    if bot.data[coinpair].macd[index - 2] < 0 and bot.data[coinpair].macd[index - 1] > 0:
        bot.plot_buy_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy_triggers[1] += utilities.TRIGGER_1
        #bot.buy(coinpair, bot.recent[coinpair][-1].close)
        return

    if bot.data[coinpair].macd[index - 1] < 0 and bot.data[coinpair].macd[index - 1] == minMACD:
        bot.plot_buy_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy_triggers[2] += utilities.TRIGGER_2
        #bot.buy(coinpair, bot.recent[coinpair][-1].close)
        return
    if bot.data[coinpair].candles[index - 2].close == minPrice and bot.data[coinpair].candles[index - 2].close < bot.data[coinpair].candles[index - 1].close:
        bot.plot_buy_triggers.append({'color': 'purple', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy_triggers[3] += utilities.TRIGGER_3
        #bot.buy(coinpair, bot.recent[coinpair][-1].close)
        return

    return

    #if sum(bot.buy_triggers) >= utilities.TRIGGER_THRESHOLD:
    if buy: bot.buy(coinpair, bot.recent[coinpair][-1].close)

    for i, strat in enumerate(bot.buy_triggers):
        bot.buy_triggers[i] -= utilities.TRIGGER_DECAY
        if bot.buy_triggers[i] < 0.0: bot.buy_triggers[i] = 0.0

    # SELLING
    #--------
    #--------
    #--------
    #--------
    '''maxPrice = -1000.0
    maxMACD = -1000.0
    minPrice = 1000.0
    minMACD = 1000.0

    for i in range(2, 24):
        if bot.data[coinpair].candles[index - i].close > maxPrice:
            maxPrice = bot.data[coinpair].candles[index - i].close
        if bot.data[coinpair].macd[index - i] > maxMACD:
            maxMACD = bot.data[coinpair].macd[index - i]
        if bot.data[coinpair].candles[index - i].close < minPrice:
            minPrice = bot.data[coinpair].candles[index - i].close
        if bot.data[coinpair].macd[index - i] < minMACD:
            minMACD = bot.data[coinpair].macd[index - i]

    if bot.data[coinpair].candles[index - 1].close / minPrice > 1.025:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[3] += utilities.TRIGGER_3

    if bot.data[coinpair].macd[index - 1] < 0: return
    if bot.data[coinpair].macd[index - 1] - bot.data[coinpair].macd[index - 2] > bot.data[coinpair].macd[index - 2] - bot.data[coinpair].macd[index - 3]: return
    if bot.data[coinpair].candles[index - 1].close < ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]: return

    if bot.data[coinpair].candles[index - 1].close > bot.data[coinpair].upperband[index - 1]:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[0] += utilities.TRIGGER_0
    if bot.data[coinpair].macd[index - 2] > 0 and bot.data[coinpair].macd[index - 1] < 0:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[1] += utilities.TRIGGER_1

    if bot.data[coinpair].macd[index - 1] > 0 and bot.data[coinpair].macd[index - 1] == maxMACD:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[2] += utilities.TRIGGER_2
    if bot.data[coinpair].candles[index - 1].close == maxPrice:
        bot.plot_sell_triggers.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[3] += utilities.TRIGGER_3'''


def check_sell(bot, position, index):
    if index < 12: return
    coinpair = position.coinpair

    maxPrice = -1000.0
    maxMACD = -1000.0
    minPrice = 1000.0
    minMACD = 1000.0

    for i in range(2, 24):
        if bot.data[coinpair].candles[index - i].close > maxPrice:
            maxPrice = bot.data[coinpair].candles[index - i].close
        if bot.data[coinpair].macd[index - i] > maxMACD:
            maxMACD = bot.data[coinpair].macd[index - i]
        if bot.data[coinpair].candles[index - i].close < minPrice:
            minPrice = bot.data[coinpair].candles[index - i].close
        if bot.data[coinpair].macd[index - i] < minMACD:
            minMACD = bot.data[coinpair].macd[index - i]
    '''if bot.data[coinpair].candles[index - 1].close / minPrice > 1.025:
        bot.plot_sell_triggers.append({'color': 'red', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[3] += utilities.TRIGGER_3
        bot.sell(position)
        return'''

    if bot.data[coinpair].macd[index - 1] < 0: return
    if bot.data[coinpair].macd[index - 1] - bot.data[coinpair].macd[index - 2] > bot.data[coinpair].macd[index - 2] - bot.data[coinpair].macd[index - 3]: return
    if bot.data[coinpair].candles[index - 1].close < ((bot.data[coinpair].upperband[index - 1] - bot.data[coinpair].lowerband[index - 1]) / 2) + bot.data[coinpair].lowerband[index - 1]: return

    if bot.data[coinpair].candles[index - 1].close > bot.data[coinpair].upperband[index - 1]:
        bot.plot_sell_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[0] += utilities.TRIGGER_0
        bot.sell(position)
        return
    if bot.data[coinpair].macd[index - 2] > 0 and bot.data[coinpair].macd[index - 1] < 0:
        bot.plot_sell_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[1] += utilities.TRIGGER_1
        bot.sell(position)
        return

    if bot.data[coinpair].macd[index - 1] > 0 and bot.data[coinpair].macd[index - 1] == maxMACD:
        bot.plot_sell_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[2] += utilities.TRIGGER_2
        bot.sell(position)
        return
    if bot.data[coinpair].candles[index - 1].close == maxPrice:
        bot.plot_sell_triggers.append({'color': 'blue', 'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.sell_triggers[3] += utilities.TRIGGER_3
        bot.sell(position)
        return

    if position.result >= 1.03:
        bot.sell(position)
        return

    return
    if sum(bot.sell_triggers) >= utilities.TRIGGER_THRESHOLD:
        bot.sell(position)
        status = 'sell'

    for index, strat in enumerate(bot.sell_triggers):
        bot.sell_triggers[index] -= utilities.TRIGGER_DECAY
        if bot.sell_triggers[index] < 0.0: bot.sell_triggers[index] = 0.0

    return

    if bot.data[position.coinpair].macd[index - 1] > bot.data[position.coinpair].macd[index - 2] and bot.data[position.coinpair].macd[index - 2] > 0.0:
        status = 'hold'
    elif bot.data[position.coinpair].macdDiff[index - 1] > bot.data[position.coinpair].macdDiff[index - 2] and bot.data[position.coinpair].macdDiff[index - 2] > 0.0:
        status = 'hold'
    else:
        status = ''

    sell = False
    if position.stopLoss: sell = True
    elif position.age > 9e5 and position.result < utilities.DROP: sell = True
    elif status == 'sell': sell = True

    if sell: bot.sell(position)
