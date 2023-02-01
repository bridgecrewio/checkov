from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.checks.object_registry import Registry as BaseCheckRegistry


class Registry(BaseCheckRegistry):
    def __init__(self) -> None:
        super().__init__(CheckType.SAST)
