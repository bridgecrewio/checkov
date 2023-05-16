from __future__ import annotations

from collections.abc import Iterable
from typing import Set

from checkov.common.bridgecrew.check_type import CheckType
from checkov.sast.checks_infra.base_registry import Registry
from checkov.sast.consts import SastLanguages


class BaseCdkRegistry(Registry):
    def __init__(
        self, checks_dir: str, temp_semgrep_rules_path: str | None = None
    ) -> None:
        super().__init__(checks_dir=checks_dir, temp_semgrep_rules_path=temp_semgrep_rules_path)
        self.report_type = CheckType.CDK

    def load_rules(
        self, frameworks: Iterable[str], sast_languages: set[SastLanguages] | None
    ) -> int:
        return self._load_checks_from_dir(directory=self.checks_dir, sast_languages=SastLanguages.set())

    def load_semgrep_checks(self, languages: Set[SastLanguages]) -> int:
        rules_loaded = 0
        for dir in self.checks_dirs_path:
            rules_loaded += self._load_checks_from_dir(dir, SastLanguages.set())
        return rules_loaded
