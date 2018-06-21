import utilities


class Balance:

    def __init__(self, client, asset):
        self.client = client
        self.asset = asset

        self.update()

    def update(self):
        try:
            self.free = self.client.get_asset_balance(asset=self.asset)['free']
        except:
            utilities.throw_error('Failed to Update Asset Balance for ' + self.asset, True)
