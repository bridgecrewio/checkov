from typing import Iterable, Dict, Optional

from checkov.common.models.enums import CheckResult
from checkov.common.typing import _CheckResult


class EnrichedSecret:
    __slots__ = ("original_secret", "bc_check_id", "resource")

    def __init__(self, original_secret: Optional[str], bc_check_id: str, resource: str):
        self.original_secret = original_secret
        self.bc_check_id = bc_check_id
        self.resource = resource


class SecretsCoordinator:
    def __init__(self) -> None:
        self._secrets: Dict[str, EnrichedSecret] = {}

    def add_secret(self, enriched_secret: EnrichedSecret, check_result: _CheckResult) -> None:
        # can be changed to any other suitable way.
        # should not have duplicates? - if duplicates allowed, implementation should be changed
        # may be saved by file type first, then by key - or any other preprocessing that may help differ the secrets.

        if check_result.get('result') == CheckResult.FAILED and enriched_secret.original_secret is not None:
            self._secrets[enriched_secret.resource] = enriched_secret

    def get_resources(self) -> Iterable[str]:
        return self._secrets.keys()


secrets_coordinator: SecretsCoordinator = SecretsCoordinator()
