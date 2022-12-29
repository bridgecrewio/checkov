from typing import Iterable, Dict


class SecretsCoordinator:
    __slots__ = ("_secrets", )

    def __init__(self) -> None:
        self._secrets: Dict[str, dict] = {}

    def add_secret(self, original_secret: str, bc_check_id: str, resource: str) -> None:
        # can be changed to any other suitable way.
        # should not have duplicates? - if duplicates allowed, implementation should be changed
        # may be saved by file type first, then by key - or any other preprocessing that may help differ the secrets.
        self._secrets[resource] = {
            "original_secret": original_secret,
            "bc_check_id": bc_check_id,
            "resource": resource,
        }

    def get_resources(self) -> Iterable[str]:
        return self._secrets.keys()

    def get_secrets(self) -> Dict[str, dict]:
        return self._secrets
