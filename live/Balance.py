class Balance:

    # Initialize a new Balance with the required information
    def __init__(self, client, asset):
        self.client = client
        self.asset = asset

        self.update()

    # Update the free amount available for the asset
    # NOTE: This has an API call
    def update(self):
        self.free = self.client.get_asset_balance(asset=self.asset)['free']
