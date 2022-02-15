class BridgecrewAuthError(Exception):
    def __init__(self, message="Authorization error accessing Bridgecrew.cloud api. Please check bc-api-key"):
        self.message = message

    def __str__(self):
        return 'BCAuthError, {0} '.format(self.message)
