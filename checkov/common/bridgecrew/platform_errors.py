from typing import List


class PlatformConnectionError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"PlatformConnectionError: {self.message}"


class BridgecrewAuthError(PlatformConnectionError):
    def __init__(self, message: str = "Authorization error accessing the platform api. Please check your API keys and "
                                      "Prisma API URL.") -> None:
        self.message = message

    def __str__(self) -> str:
        return f"BCAuthError: {self.message}"


class ModuleNotEnabledError(Exception):
    def __init__(self, message: str, unsupported_frameworks: List[str]) -> None:
        self.message = message
        self.unsupported_frameworks = unsupported_frameworks

    def __str__(self) -> str:
        return f"ModuleNotEnabledError: {self.message}"
