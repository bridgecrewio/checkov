from typing import Optional, Iterable

from detect_secrets.core.potential_secret import PotentialSecret

from checkov.common.bridgecrew.severities import Severity
from checkov.common.typing import _CheckResult


class EnrichedSecret:
    def __init__(self, potential_secret: PotentialSecret, check_id: str, bc_check_id: str, secret_key: str,
                 severity: Optional[Severity], result: _CheckResult, code_block: list[tuple[int, str]],
                 resource: str):
        self.potential_secret = potential_secret
        self.check_id = check_id
        self.bc_check_id = bc_check_id
        self.secret_key = secret_key
        self.severity = severity
        self.result = result
        self.code_block = code_block
        self.resource = resource


class SecretsCoordinator:
    def __init__(self):
        self._secrets = {}

    def add_secret(self, enriched_secret: EnrichedSecret) -> None:
        # can be changed to any other suitable way.
        # should not have duplicates? - if duplicates allowed, implementation should be changed
        # may be saved by file type first, then by key - or any other preprocessing that may help differ the secrets.
        self._secrets[enriched_secret.secret_key] = enriched_secret

    def get_secrets(self) -> dict[str, EnrichedSecret]:
        return self._secrets

    def get_resources(self) -> Iterable[str]:
        return {secret.resource for secret in self._secrets.values()}


secrets_coordinator = SecretsCoordinator()



