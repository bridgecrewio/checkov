from abc import abstractmethod
from typing import Dict, Any

from checkov.common.output.record import Record
from checkov.policies_3d.checks_infra.base_check import Base3dPolicyCheck
from checkov.sca_image.models import ReportCVE


class Base3dPolicyCheckParser:
    def __init__(self, raw_check: dict[str, dict[str, Any]]):
        if not raw_check:
            return

        self.schema_version = raw_check.get('version')
        self.check_definition = raw_check.get('definition')
        self.metadata = raw_check.get('metadata')

    @abstractmethod
    def parse_raw_check(self, raw_check: Dict[str, Dict[str, Any]], **kwargs: Any) -> Base3dPolicyCheck:
        pass

    def _fill_check_metadata(self, check: Base3dPolicyCheck) -> None:
        check.id = self.metadata.get("id", "")
        check.name = self.metadata.get("name", "")
        check.category = self.metadata.get("category", "")
        check.guideline = self.metadata.get("guideline", "")

    def parse(self, iac_records: list[Record], secrets_records: list[Record], cves_reports: list[ReportCVE]) -> Base3dPolicyCheck | None:
        if self.schema_version == 'v1':
            return self._parse_check_v1()

    @abstractmethod
    def _parse_check_v1(self, iac_records: list[Record], secrets_records: list[Record], cves_reports: list[ReportCVE]) -> Base3dPolicyCheck:
        pass
