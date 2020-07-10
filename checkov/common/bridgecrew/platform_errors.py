class BridgecrewAuthError(Exception):
    def __init__(self):
        self.message = "Authorization error accessing Bridgecrew.cloud api. Please check bc-api-key"

    def __str__(self):
        return 'BCAuthError, {0} '.format(self.message)
