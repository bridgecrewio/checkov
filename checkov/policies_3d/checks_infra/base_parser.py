from __future__ import annotations
from abc import abstractmethod
from typing import Dict, Any

from checkov.common.output.record import Record
from checkov.policies_3d.checks_infra.base_check import Base3dPolicyCheck
import json


class Base3dPolicyCheckParser:
    def __init__(self, raw_check: dict[str, Any] | None = None):
        if not raw_check:
            return

        self.raw_check = raw_check

        check_code = json.loads(raw_check.get('code', ''))
        self.schema_version = check_code.get('version')
        self.check_definition = check_code.get('definition')

    @abstractmethod
    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> Base3dPolicyCheck:
        pass

    def _fill_check_metadata(self, check: Base3dPolicyCheck) -> None:
        check.id = self.raw_check.get("id", "")
        check.name = self.raw_check.get("name", "")
        check.category = self.raw_check.get("category", "")
        check.guideline = self.raw_check.get("guideline", "")

    def parse(self, iac_records: list[Record] | None = None,
              secrets_records: list[Record] | None = None,
              cves_reports: list[dict[str, Any]] | None = None) -> Base3dPolicyCheck | None:
        if self.schema_version == 'v1':
            return self._parse_check_v1(iac_records or [], secrets_records or [], cves_reports or [])

        return None

    @abstractmethod
    def _parse_check_v1(self, iac_records: list[Record], secrets_records: list[Record], cves_reports: list[dict[str, Any]]) -> Base3dPolicyCheck:
        pass
