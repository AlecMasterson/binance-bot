class Balance:

    # Initialize a new Balance with the required information
    def __init__(self, client, asset, val):
        self.client = client
        self.asset = asset

        # Update the amount available.
        # If using this offline, manually set the starting value.
        if self.client != None: self.update()
        else: self.free = val

    # Update the free amount available for the asset
    # NOTE: This has an API call
    def update(self):
        self.free = self.client.get_asset_balance(asset=self.asset)['free']
