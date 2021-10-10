class BridgecrewAuthError(Exception):
    def __init__(self):
        self.message = "Authorization error accessing Bridgecrew.cloud api. Please check bc-api-key"

    def __str__(self):
        return f'BCAuthError, {self.message} '
