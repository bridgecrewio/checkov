from __future__ import annotations
from typing import Iterable
from typing_extensions import TypedDict


class EnrichedSecret(TypedDict):
    original_secret: str
    bc_check_id: str
    resource: str
    line_number: int


class SecretsCoordinator:
    __slots__ = ("_secrets", )

    def __init__(self) -> None:
        self._secrets: list[EnrichedSecret] = []

    def add_secret(self, enriched_secret: EnrichedSecret) -> None:
        # should not have duplicates? - if duplicates allowed, implementation should be changed
        # may be saved by file type first, then by key - or any other preprocessing that may help differ the secrets.
        self._secrets.append(enriched_secret)

    def get_resources(self) -> Iterable[str]:
        return [enriched_secret["resource"] for enriched_secret in self._secrets]

    def get_secrets(self) -> list[EnrichedSecret]:
        return self._secrets
