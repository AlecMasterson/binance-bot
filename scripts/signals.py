def rsi(data):
    if float(data.at[len(data) - 1, 'RSI']) < 20.0: return True
    return False


def lowerband(data):
    if float(data.at[len(data) - 1, 'CLOSE']) < float(data.at[len(data) - 1, 'LOWERBAND']): return True
    return False
