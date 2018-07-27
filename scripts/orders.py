import helpers, argparse, pandas, sys, os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + './..'))
import utilities


def get_order(client, order_id, symbol):
    try:
        return client.get_order(symbol=symbol, orderId=order_id)
    except:
        utilities.throw_error('Failed to Retrieve Order from Binance API', True)


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB with Current Orders').parse_args()

    client = helpers.connect_binance()

    orders = helpers.read_csv('data/online/orders.csv', True)
    orders_temp = helpers.read_csv('data/online/orders_temp.csv', True)

    for index, order_temp in orders_temp.iterrows():
        if not (orders['order_id'] == order_temp['order_id']).any():
            new_order = get_order(client, order_temp['order_id'], order_temp['symbol'])
            orders = orders.append(
                {
                    'order_id': new_order['orderId'],
                    'symbol': new_order['symbol'],
                    'side': new_order['side'],
                    'status': new_order['status'],
                    'time': new_order['time'],
                    'executedQty': new_order['executedQty']
                },
                ignore_index=True)
            helpers.to_csv('data/online/orders.csv', orders)

    for index, order in orders.iterrows():
        order_updated = get_order(client, order['order_id'], order['symbol'])
        order['status'] = order_updated['status']
        order['time'] = order_updated['time']
        order['executedQty'] = order_updated['executedQty']

    helpers.to_csv('data/online/orders.csv', orders)
