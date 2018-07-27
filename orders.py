import utilities, argparse, pandas
from binance.client import Client


def update_order(order_id, symbol):
    try:
        return client.get_order(symbol=symbol, orderId=order_id)
    except:
        utilities.throw_error('Failed to Retrieve Order from Binance API', True)


def save_orders(orders):
    try:
        orders.to_csv('data/online/orders.csv', index=False)
    except:
        utilities.throw_info('Failed to Update File', True)


if __name__ == '__main__':
    argparse.ArgumentParser(description='Used for Updating the DB of Current Orders').parse_args()

    try:
        client = Client(utilities.PUBLIC_KEY, utilities.SECRET_KEY)
    except:
        utilities.throw_error('Failed to Connect to the Binance API', True)

    try:
        orders = pandas.read_csv('data/online/orders.csv')
        orders_temp = pandas.read_csv('data/online/orders_temp.csv')
    except FileNotFoundError:
        orders = pandas.DataFrame(columns=['order_id', 'symbol', 'side', 'status', 'time', 'executedQty'])
        orders_temp = pandas.DataFrame(columns=['order_id', 'symbol'])
        try:
            orders.to_csv('data/online/orders.csv', index=False)
            orders_temp.to_csv('data/online/orders_temp.csv', index=False)
        except:
            utilities.throw_info('Failed to Create Missing Files', True)
    except:
        utilities.throw_error('Failed to Load Data Files', True)

    for index, order_temp in orders_temp.iterrows():
        if not (orders['order_id'] == order_temp['order_id']).any():
            new_order = update_order(order_temp['order_id'], order_temp['symbol'])
            orders = orders.append({
                'order_id': new_order['orderId'],
                'symbol': new_order['symbol'],
                'side': new_order['side'],
                'status': new_order['status'],
                'time': new_order['time'],
                'executedQty': new_order['executedQty']
            })
            save_orders(orders)

    for index, order in orders.iterrows():
        order_updated = update_order(order['order_id'], order['symbol'])
        order['status'] = order_updated['status']
        order['time'] = order_updated['time']
        order['executedQty'] = order_updated['executedQty']

    save_orders(orders)
