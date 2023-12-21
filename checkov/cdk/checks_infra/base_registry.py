from __future__ import annotations


from checkov.common.bridgecrew.check_type import CheckType
from checkov.sast.checks_infra.base_registry import Registry


class BaseCdkRegistry(Registry):
    def __init__(self, checks_dir: str) -> None:
        super().__init__(checks_dir=checks_dir)
        self.report_type = CheckType.CDK
