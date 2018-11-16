def rsi(data):
    if len(data) < 3: return False

    if float(data[-1]['RSI']) < 25.0:
        if float(data[-3]['RSI']) > float(data[-2]['RSI']) and float(data[-2]['RSI']) > float(data[-1]['RSI']):
            if float(data[-2]['RSI']) - float(data[-1]['RSI']) > float(data[-3]['RSI']) - float(data[-2]['RSI']): return True
    return False


def rsi_2(data):
    smallest_rsi = min([row['RSI'] for row in data])
    if smallest_rsi < 28.0 and data[-1]['RSI'] > 30.0: return True
    return False


def cheating(data):
    if data[-1]['FUTURE_POTENTIAL'] > 1.02: return True
    return False


def lowerband(data):
    if float(data[-1]['CLOSE']) < float(data[-1]['LOWERBAND']): return True
    return False
