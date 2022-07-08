class BridgecrewAuthError(Exception):
    def __init__(self, message: str = "Authorization error accessing Bridgecrew.cloud api. Please check bc-api-key") -> None:
        self.message = message

    def __str__(self) -> str:
        return f"BCAuthError, {self.message} "
