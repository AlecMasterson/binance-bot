from binance.client import Client
import argparse, pandas, json
import utilities

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A Simple Script to Download and Save Coinpair Data')
    parser.add_argument('-c', '--coinpairs', help='list of Coinpairs to get data for', nargs='+', type=str, action='append', dest='coinpairs', required=True)
    args = parser.parse_args()

    try:
        client = Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
    except:
        utilities.throw_error('Failed to Connect to Binance API', True)
    utilities.throw_info('Successfully Finished Connecting to Binance Client')

    for coinpair in args.coinpairs[0]:
        try:
            utilities.throw_info('Getting Historical Data for ' + coinpair + '...')
            data = pandas.DataFrame(client.get_historical_klines(symbol=coinpair, interval=utilities.TIME_INTERVAL, start_str=utilities.START_DATE), columns=utilities.COLUMN_STRUCTURE)
            data.to_csv('data/history/' + coinpair + '.csv', index=False)
        except:
            utilities.throw_error('Failed to Update Historical Data for ' + coinpair, False)

        try:
            utilities.throw_info('Getting Coinpair Info for ' + coinpair + '...')
            info = client.get_symbol_info(coinpair)
            with open('data/coinpair/' + coinpair + '.json', 'w') as json_file:
                json.dump(info, json_file)
        except:
            utilities.throw_error('Failed to Update Coinpair Info for ' + coinpair, False)

    utilities.throw_info('Successfully Finished Updating all Coinpairs')
