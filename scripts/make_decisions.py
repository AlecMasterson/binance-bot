from util.decor import main
import models.Decision
import models.History
import models.Symbol
import util.db
import util.util
import argparse


@main(name='make_decisions')
def make_decisions(*, logger):
    db = util.db.db_connect(logger=logger)
    config = util.util.load_config(logger=logger)
    tradingModels = util.util.load_trading_models(logger=logger)

    symbols = models.Symbol.get_active(logger=logger, db=db)['name']

    logger.info('Making Trading Decisions for {} Symbol(s) with {} Trading-Model(s)...'.format(len(symbols), len(tradingModels)))
    for symbol in symbols:
        outerLogPrefix = '(Symbol) - ({}) - '.format(symbol)
        try:
            data = models.History.get_history(logger=logger, db=db, symbol=symbol)
            if len(data) == 0:
                logger.error('{}No Historical Pricing Data Found'.format(outerLogPrefix))
                continue

            mostRecentCloseTime = max(data['close_time']).to_pydatetime()
            logger.info('{}Making Decision for CloseTime \'{}\''.format(outerLogPrefix, mostRecentCloseTime))

            for model in tradingModels:
                innerLogPrefix = '(Symbol,Model) - ({},{}) - '.format(symbol, model.__name__)
                try:
                    currentDecision = models.Decision.get_choice(
                        logger=logger, db=db,
                        model=model.__name__,
                        symbol=symbol,
                        closeTime=mostRecentCloseTime
                    )

                    if currentDecision is not None:
                        logger.warning('{}Decision Already Made. Choice = {}'.format(innerLogPrefix, currentDecision.choice))
                        continue

                    choice = model.analyze(config=config, data=data)
                    logger.info('{}Choice = {}'.format(innerLogPrefix, choice))

                    models.Decision.insert_decision(
                        logger=logger,
                        db=db,
                        model=model.__name__,
                        symbol=symbol,
                        closeTime=mostRecentCloseTime,
                        choice=choice
                    )
                except Exception as e:
                    logger.exception('{}Unexpected Error:\n{}'.format(innerLogPrefix, e))
        except Exception as e:
            logger.exception('{}Unexpected Error:\n{}'.format(outerLogPrefix, e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Utilize All Trading-Models to Make Trading Decisions on All Active Symbols')
    parser.parse_args()
    make_decisions()
