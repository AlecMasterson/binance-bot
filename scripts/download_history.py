from util.decor import main
import util.util
import util.db
import argparse
import ta


def download(*, logger, config, client, db, symbol):
    for width in config['symbol_data']['widths']:
        data = util.util.get_historical_data(
            logger=logger,
            client=client,
            symbol=symbol,
            width=width,
            startDate=config['symbol_data']['start_date']
        )

        util.db.insert_data(
            db=db,
            tableName=config['database_details']['tables']['history'],
            qualifier='{}_{}'.format(symbol, width),
            data=data
        )

        data.to_csv(
            util.util.get_file_path(
                create=True,
                directoryTree=(config['export_directories']['symbol_data'], symbol),
                fileName='{}.csv'.format(width)
            ),
            index=False
        )


@main(name='download_history')
def run(symbols, logger, config):
    client = util.util.binance_connect(logger=logger)
    db = util.util.db_connect(logger=logger)

    logger.info('Downloading {} Symbols...'.format(len(symbols)))
    errors = util.util.track_errors(
        f=download,
        items=symbols,
        keyName='symbol',
        logger=logger, config=config, client=client, db=db
    )

    if len(errors) > 0:
        logger.error('Error(s) Downloading Historical Data for {} Symbol(s):\n{}'.format(len(errors), '\n'.join(errors)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Used for Downloading Historical Data from the Binance Exchange')
    parser.add_argument('-s', '--symbols', help='a list of symbols to download', type=str, nargs='+', dest='SYMBOLS', required=True)
    run(parser.parse_args().SYMBOLS)
