from binance.client import Client
from components.Candle import Candle
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor
import utilities


class Sockets:

    def __init__(self, bot):
        self.bot = bot

        self.manager = BinanceSocketManager(bot.client)
        for coinpair in utilities.COINPAIRS:
            self.manager.start_kline_socket(coinpair, self.kline_callback, interval=utilities.TIME_INTERVAL)

        self.manager.start()

    def kline_callback(self, message):
        if message['e'] == 'error':
            self.close_socket_manager()
            utilities.throw_error('Error in kline Socket Connection', True)
        else:
            if message['k']['x']:
                if message['k']['t'] == self.bot.data[message['s']].candles[-1].openTime: return

                # TODO: Add numTrades and volume.
                self.bot.data[message['s']].add_candle(Candle(message['k']['t'], message['k']['o'], message['k']['h'], message['k']['l'], message['k']['c'], message['k']['T']))

            self.bot.recent[message['s']].append({'time': int(message['k']['t']), 'price': float(message['k']['c'])})
            if len(self.bot.recent[message['s']]) > 50: self.bot.recent[message['s']].pop(0)

    def close_socket_manager(self):
        try:
            self.manager.close()
            utilities.throw_info('Successfully Closed Socket Manager')
        except:
            utilities.throw_info('Failed to Close Socket Manager')
        reactor.stop()
