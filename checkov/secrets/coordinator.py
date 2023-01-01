from typing import Iterable, Dict
from typing_extensions import TypedDict


class EnrichedSecret(TypedDict):
    original_secret: str
    bc_check_id: str
    resource: str


class SecretsCoordinator:
    __slots__ = ("_secrets", )

    def __init__(self) -> None:
        self._secrets: Dict[str, EnrichedSecret] = {}

    def add_secret(self, enriched_secret: EnrichedSecret) -> None:
        # should not have duplicates? - if duplicates allowed, implementation should be changed
        # may be saved by file type first, then by key - or any other preprocessing that may help differ the secrets.
        self._secrets[enriched_secret['resource']] = enriched_secret

    def get_resources(self) -> Iterable[str]:
        return self._secrets.keys()

    def get_secrets(self) -> Dict[str, EnrichedSecret]:
        return self._secrets
