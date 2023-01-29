from __future__ import annotations

import json
import logging
import typing
from abc import abstractmethod
from typing import Dict, List, Any, Union

from checkov.common.models.enums import CheckResult

if typing.TYPE_CHECKING:
    from cloudsplaining.scan.policy_document import PolicyDocument


class BaseTerraformCloudsplainingIAMScanner:
    # creating a PolicyDocument is computational expensive,
    # therefore a cache is defined at class level
    policy_document_cache: Dict[str, PolicyDocument] = {}  # noqa: CCE003

    def scan_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        if self.should_scan_conf(conf):
            try:
                if self.cache_key not in BaseTerraformCloudsplainingIAMScanner.policy_document_cache.keys():
                    policy = self.convert_to_iam_policy(conf)
                    BaseTerraformCloudsplainingIAMScanner.policy_document_cache[self.cache_key] = policy
                violations = self.cloudsplaining_analysis(
                    BaseTerraformCloudsplainingIAMScanner.policy_document_cache[self.cache_key]
                )
            except Exception:
                # this might occur with templated iam policies where ARN is not in place or similar
                logging.debug(f"could not run cloudsplaining analysis on policy {conf}")
                return CheckResult.UNKNOWN
            if violations:
                logging.debug(f"detailed cloudsplainging finding: {json.dumps(violations, indent=2, default=str)}")
                return CheckResult.FAILED
        return CheckResult.PASSED

    @property
    @abstractmethod
    def cache_key(self) -> str:
        pass

    @abstractmethod
    def should_scan_conf(self, conf: Dict[str, List[Any]]) -> bool:
        pass

    @abstractmethod
    def convert_to_iam_policy(self, conf: Dict[str, List[Any]]) -> PolicyDocument:
        pass

    @abstractmethod
    def cloudsplaining_analysis(self, policy: PolicyDocument) -> Union[List[str], List[Dict[str, Any]]]:
        raise NotImplementedError()
