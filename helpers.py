import pandas, math


# Round down x to the nearest 0.001 (Binance Trade Minimum)
# x - The number to round down
def round_down(x):
    return float(math.floor(x * 1000) / 1000)


# Return the resulting BTC and ALT wallet values if you were to buy
# btc - Current BTC wallet value
# alt - Current ALT wallet value
# price - Price at which to trade
# fee - Percent fee for transaction
# quantity - Percentage of BTC/ALT to trade with
def predict_buy(btc, alt, price, fee, quantity):
    return {'btc': btc - round_down(btc * quantity), 'alt': alt + round_down(btc * quantity) / price * (1.0 - fee)}


# Return the resulting BTC and ALT wallet values if you were to sell
# btc - Current BTC wallet value
# alt - Current ALT wallet value
# price - Price at which to trade
# fee - Percent fee for transaction
# quantity - Percentage of BTC/ALT to trade with
def predict_sell(btc, alt, price, fee, quantity):
    return {'alt': alt - round_down(alt * quantity), 'btc': btc + round_down(alt * quantity) * price * (1.0 - fee)}


# Return DataFrame with trading-data after submitting a buy order
# trading - The trading-data DataFrame
# time - Current time (in milliseconds) at which to buy
# price - Price at which to trade
# fee - Percent fee for transaction
# quantity - Percentage of BTC/ALT to trade with
def buy(trading, time, price, fee, quantity):
    # If the current BTC wallet value is too low to make a buy order, cancel transaction.
    if round_down(trading.iloc[-1]['btc'] * quantity) == 0.0: return trading
    return trading.append(
        {
            'type': 'buy',
            'time': time,
            'price': price,
            'quantity': quantity,
            'btc': trading.iloc[-1]['btc'] - round_down(trading.iloc[-1]['btc'] * quantity),
            'alt': trading.iloc[-1]['alt'] + round_down(trading.iloc[-1]['btc'] * quantity) / price * (1.0 - fee)
        },
        ignore_index=True)


# Return DataFrame with trading-data after submitting a sell order
# trading - The trading-data DataFrame
# time - Current time (in milliseconds) at which to buy
# price - Price at which to trade
# fee - Percent fee for transaction
# quantity - Percentage of BTC/ALT to trade with
def sell(trading, time, price, fee, quantity):
    # If the current ALT wallet value is too low to make a sell order, cancel transaction.
    if round_down(trading.iloc[-1]['alt'] * quantity) == 0.0: return trading
    return trading.append(
        {
            'type': 'sell',
            'time': time,
            'price': price,
            'quantity': quantity,
            'btc': trading.iloc[-1]['btc'] + round_down(trading.iloc[-1]['alt'] * quantity) / price * (1.0 - fee),
            'alt': trading.iloc[-1]['alt'] - round_down(trading.iloc[-1]['alt'] * quantity)
        },
        ignore_index=True)


# Return combined wallet total of BTC and ALT in the form of BTC
# values - A DataFrame entry from the trading-data DataFrame
def combined_total(values):
    return values['btc'] + values['alt'] * values['price']
