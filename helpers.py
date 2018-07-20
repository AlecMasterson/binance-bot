import numpy as np
import pandas, math
import numba


# Round down x to the nearest 0.001 (Binance Trade Minimum)
# x - The number to round down
@numba.jit
def round_down(x):
    return float(math.floor(x * 1000) / 1000)


# Return DataFrame with trading-data after submitting a buy order
# trading - The trading-data DataFrame
# coinPair - The coin-pair exchange being made
# time - Current time (in milliseconds) at which to buy
# price - Price at which to trade
# quantity - Percentage of source wallet to trade with
# fee - Percent fee for transaction
def buy(trading, coinPair, time, price, quantity, fee):
    # Determine the source currency of the trade.
    if coinPair.endswith('BTC'): source = 'btc'
    else: source = 'eth'

    # Determine the destination currency of the trade.
    if coinPair.startswith('BTC'): dest = 'btc'
    elif coinPair.startswith('ETH'): dest = 'eth'
    else: dest = coinPair

    # If the current source wallet value is too low to make a buy order, cancel transaction.
    if round_down(trading.iloc[-1][source] * quantity) == 0.0: return trading

    # Actually append the transaction with the new wallet values.
    trading = trading.append(
        {
            'type': 'buy',
            'coinPair': coinPair,
            'time': time,
            'price': price,
            'quantity': quantity,
            'fee': round_down(trading.iloc[-1][source] * quantity) / price * fee,
            source: trading.iloc[-1][source] - round_down(trading.iloc[-1][source] * quantity),
            dest: trading.iloc[-1][dest] + round_down(trading.iloc[-1][source] * quantity) / price * (1.0 - fee)
        },
        ignore_index=True)

    # Fill all values unrelated to this trade with it's last known value.
    trading = trading.replace(np.nan, np.nan).ffill()

    return trading


# Return DataFrame with trading-data after submitting a sell order
# trading - The trading-data DataFrame
# coinPair - The coin-pair exchange being made
# time - Current time (in milliseconds) at which to sell
# price - Price at which to trade
# quantity - Percentage of source wallet to trade with
# fee - Percent fee for transaction
def sell(trading, coinPair, time, price, quantity, fee):
    # Determine the source currency of the trade.
    if coinPair.endswith('BTC'): source = 'btc'
    else: source = 'eth'

    # Determine the destination currency of the trade.
    if coinPair.startswith('BTC'): dest = 'btc'
    elif coinPair.startswith('ETH'): dest = 'eth'
    else: dest = coinPair

    # If the current source wallet value is too low to make a sell order, cancel transaction.
    if round_down(trading.iloc[-1][dest] * quantity) == 0.0: return trading

    # Actually append the transaction with the new wallet values.
    trading = trading.append(
        {
            'type': 'sell',
            'coinPair': coinPair,
            'time': time,
            'price': price,
            'quantity': quantity,
            'fee': round_down(trading.iloc[-1][dest] * quantity) / price * fee,
            source: trading.iloc[-1][source] + round_down(trading.iloc[-1][dest] * quantity) * price * (1.0 - fee),
            dest: trading.iloc[-1][dest] - round_down(trading.iloc[-1][dest] * quantity)
        },
        ignore_index=True)

    # Fill all values unrelated to this trade with it's last known value.
    trading = trading.replace(np.nan, np.nan).ffill()

    return trading


def predict_loss(trading, coinPair, price, quantity):
    buyRow = None
    for index, row in trading.iterrows():
        if row['type'] == 'buy' and row['coinPair'] == coinPair: buyRow = row
    if buyRow is None: return 1.0
    return (trading.iloc[-1][coinPair] * price * quantity) / (buyRow[coinPair] * buyRow['price'])


# Return combined initial wallet total value in the form of BTC
# data - Combined price-data of all coin-pairs
# trading - The trading-data DataFrame
def starting_total(data, trading):
    return trading.iloc[0]['btc'] + trading.iloc[0]['eth'] * data.iloc[0]['open-ETHBTC']


# Return combined wallet total value in the form of BTC
# data - Combined price-data of all coin-pairs
# trading - The trading-data DataFrame
# coinPairs - All coin-pairs involved
def combined_total(data, trading, coinPairs):
    btc = trading.iloc[-1]['btc']
    eth = trading.iloc[-1]['eth']
    for coinPair in coinPairs:
        if coinPair.startswith('BTC') or coinPair.startswith('ETH'): continue

        if coinPair.endswith('BTC'): btc += trading.iloc[-1][coinPair] * data.iloc[-1]['close-' + coinPair]
        else: eth += trading.iloc[-1][coinPair] * data.iloc[-1]['close-' + coinPair]
    return btc + eth * data.iloc[-1]['close-ETHBTC']


# Return an array with the new wallet values for BTC and ALT after submitting a buy order
# btc - Current BTC wallet value
# alt - Current ALT wallet value
# price - Price at which to trade
# fee - Percent fee for transaction
@numba.jit
def buy_env(btc, alt, price, fee):
    return [btc - round_down(btc), alt + round_down(btc) / price * (1.0 - fee)]


# Return an array with the new wallet values for BTC and ALT after submitting a sell order
# btc - Current BTC wallet value
# alt - Current ALT wallet value
# price - Price at which to trade
# fee - Percent fee for transaction
@numba.jit
def sell_env(btc, alt, price, fee):
    return [btc + round_down(alt) * price * (1.0 - fee), alt - round_down(alt)]


# Return combined wallet total of BTC and ALT in the form of BTC
# btc - Current BTC wallet value
# alt - Current ALT wallet value
# price - Current price of the exchange
@numba.jit
def combined_total_env(btc, alt, price):
    return btc + alt * price
