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
    if index < 2: return

    if within_range(bot.data[coinpair].candles[index - 1].low, bot.data[coinpair].lowerband[index - 1], -0.002):
        bot.triggers[0] = 1 / utilities.NUM_TRIGGERS
    if bot.data[coinpair].candles[index - 1].close < bot.data[coinpair].lowerband[index - 1]:
        bot.triggers[1] = 1 / utilities.NUM_TRIGGERS
    if bot.data[coinpair].macd[index - 2] < 0 and bot.data[coinpair].macd[index - 1] > 0:
        bot.triggers[2] = 1 / utilities.NUM_TRIGGERS

    if sum(bot.triggers) >= utilities.TRIGGER_THRESHOLD:
        bot.testingB.append({'time': bot.recent[coinpair][-1].closeTime, 'price': bot.recent[coinpair][-1].close})
        bot.buy(coinpair, bot.recent[coinpair][-1].close)

    for index, strat in enumerate(bot.triggers):
        bot.triggers[index] -= utilities.TRIGGER_DECAY
        if bot.triggers[index] < 0.0: bot.triggers[index] = 0.0


def check_sell(bot, position, index):
    if index < 2: return

    if bot.data[position.coinpair].macd[index - 1] > bot.data[position.coinpair].macd[index - 2] and bot.data[position.coinpair].macd[index - 2] > 0.0:
        status = 'hold'
    elif bot.data[position.coinpair].macdDiff[index - 1] > bot.data[position.coinpair].macdDiff[index - 2] and bot.data[position.coinpair].macdDiff[index - 2] > 0.0:
        status = 'hold'
    else:
        status = ''

    sell = False
    if status != 'hold' and position.stopLoss: sell = True
    elif position.age > 9e5 and position.result < utilities.DROP: sell = True
    elif status == 'sell': sell = True

    if sell: bot.sell(position)
