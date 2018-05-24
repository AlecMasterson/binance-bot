class Balance:

    # Initialize a new Balance with the required information
    def __init__(self, client, online, asset, val):
        self.client = client
        self.online = True
        self.asset = asset

        # Update the amount available.
        self.update(val)

    # Update the free amount available for the asset
    # This chooses between online and offline mode
    # val - The optional new amount of available asset
    def update(self, val):
        if self.online: self.update_online()
        else self.update_offline(val)

    # The online updating function
    # NOTE: This has an API call
    def update_online(self):
        self.free = self.client.get_asset_balance(asset=self.asset)['free']

    # The offline updating function
    # val - The new amount available
    def update_offline(self, val):
        self.free = val
