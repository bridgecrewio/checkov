from typing import Iterable, Dict, Optional


class EnrichedSecret:
    __slots__ = ("original_secret", "bc_check_id", "resource")

    def __init__(self, original_secret: Optional[str], bc_check_id: str, resource: str) -> None:
        self.original_secret = original_secret
        self.bc_check_id = bc_check_id
        self.resource = resource


class SecretsCoordinator:
    __slots__ = ("_secrets", )

    def __init__(self) -> None:
        self._secrets: Dict[str, EnrichedSecret] = {}

    def add_secret(self, enriched_secret: EnrichedSecret) -> None:
        # can be changed to any other suitable way.
        # should not have duplicates? - if duplicates allowed, implementation should be changed
        # may be saved by file type first, then by key - or any other preprocessing that may help differ the secrets.
        self._secrets[enriched_secret.resource] = enriched_secret

    def get_resources(self) -> Iterable[str]:
        return self._secrets.keys()
