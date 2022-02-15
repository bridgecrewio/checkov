class BridgecrewAuthError(Exception):
    def __init__(self, message: str = "Authorization error accessing Bridgecrew.cloud api. Please check bc-api-key") -> None:
        self.message: str = message

    def __str__(self) -> str:
        return 'BCAuthError, {0} '.format(self.message)
