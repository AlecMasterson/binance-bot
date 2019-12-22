import util.binance
from util.decor import main


@main(name='test')
def run(*, logger, config):
    logger.info('test')
    client = util.binance.binance_connect(logger=logger)


run()
