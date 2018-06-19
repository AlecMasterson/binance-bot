import utilities


class Balance:

    def __init__(self, client, asset, free=None):
        self.client = client
        self.asset = asset

        if self.client == None and free != None: self.free = free
        else: self.update()

    def update(self, amount=None):
        if amount != None: self.free += amount
        else:
            try:
                self.free = self.client.get_asset_balance(asset=self.asset)['free']
            except:
                utilities.throw_error('Failed to Update Asset ' + self.asset + ' Balance', True)
