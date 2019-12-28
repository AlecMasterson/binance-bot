from util.decor import main
from models.Decision import Decision
from models.History import History
import util.db
import util.util
import argparse
import datetime
import json
import os
import pkgutil
import tqdm
import trading_models


@main(name='trading_decisions')
def run(*, logger):
    db = util.db.db_connect(logger=logger)
    config = json.load(open('{}/scripts/config.json'.format(os.environ['PROJECT_PATH'])))

    models = []
    for loader, name, is_pkg in pkgutil.walk_packages(trading_models.__path__):
        models.append(loader.find_module(name).load_module(name))
    if len(models) == 0:
        logger.warning('No Trading-Models Found')
        return
    logger.info('Utilizing {} Different Trading-Models'.format(len(models)))

    symbols = [result.symbol for result in db.query(History.symbol).distinct()]
    if len(symbols) == 0:
        logger.warning('No Symbols Found')
        return
    logger.info('Analyzing {} Symbols'.format(len(symbols)))

    for symbol in tqdm.tqdm(symbols):
        try:
            data = util.db.get_data(logger=logger, db=db, model=History, query={'symbol': symbol})

            if not util.util.is_recent(data=data):
                logger.warning('(Symbol,Model) - ({},) - Stale Data'.format(symbol))
                continue

            for model in models:
                try:
                    decision = Decision(
                        model.__name__,
                        symbol,
                        datetime.datetime.now(),
                        model.analyze(config=config, data=data)
                    )
                    logger.info('(Symbol,Model) - ({},{}) - Choice: {}'.format(symbol, model.__name__, decision.choice))

                    db.add(decision)
                    db.commit()
                except Exception as ee:
                    logger.exception('(Symbol,Model) - ({},{}) - Unknown Error: {}'.format(symbol, model.__name__, ee))
        except Exception as e:
            logger.exception('(Symbol,Model) - ({},) - Unknown Error: {}'.format(symbol, e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Utilize All Trading Models to Make a Trading Decision on All Symbols')
    parser.parse_args()
    run()
