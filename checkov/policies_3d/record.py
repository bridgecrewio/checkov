from __future__ import annotations
from typing import List, Dict, Any, Tuple, Optional

from checkov.common.bridgecrew.severities import Severity
from checkov.common.output.record import Record
from checkov.common.typing import _CheckResult


class Policy3dRecord(Record):
    def __init__(self,
                 check_id: str,
                 bc_check_id: str,
                 check_name: str,
                 check_result: _CheckResult,
                 code_block: List[Tuple[int, str]],
                 file_path: str,
                 file_line_range: List[int],
                 resource: str,
                 evaluations: Optional[Dict[str, Any]],
                 check_class: str,
                 file_abs_path: str,
                 severity: Optional[Severity],
                 vulnerabilities: List[Dict[str, Any]],
                 iac_records: List[Record],
                 composed_from_iac_records: List[Record],
                 composed_from_secrets_records: list[Record],
                 composed_from_cves: list[Dict[str, Any]]
                 ) -> None:
        super().__init__(
            check_id=check_id,
            bc_check_id=bc_check_id,
            check_name=check_name,
            check_result=check_result,
            code_block=code_block,
            file_path=file_path,
            file_line_range=file_line_range,
            resource=resource,
            evaluations=evaluations,
            check_class=check_class,
            file_abs_path=file_abs_path,
            severity=severity,
        )
        self.vulnerabilities = vulnerabilities
        self.iac_records = iac_records
        self.composed_from_iac_records = composed_from_iac_records
        self.composed_from_secrets_records = composed_from_secrets_records
        self.composed_from_cves = composed_from_cves
