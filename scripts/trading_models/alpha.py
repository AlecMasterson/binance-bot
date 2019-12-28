import util.util
from models.Choice import Choice
import random


def analyze(*, config, data):
    val = random.randint(0, 10)
    if val < 4:
        return Choice.BUY
    if val < 7:
        return Choice.SELL
    return Choice.HOLD
