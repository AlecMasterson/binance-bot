import util.util
import random


def analyze(*, config, data):
    val = random.randint(0, 10)
    if val < 4:
        return 'BUY'
    if val < 7:
        return 'SELL'
    return 'HOLD'
