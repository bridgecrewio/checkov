from __future__ import annotations
from typing import Optional, List, Tuple, Dict, Any

from checkov.common.bridgecrew.severities import Severity

from checkov.common.output.record import Record
from checkov.common.typing import _CheckResult


class SecretsRecord(Record):
    def __init__(self,
                 check_id: str,
                 check_name: str,
                 check_result: _CheckResult,
                 code_block: List[Tuple[int, str]],
                 file_path: str,
                 file_line_range: List[int],
                 resource: str,
                 evaluations: Optional[Dict[str, Any]],
                 check_class: str,
                 file_abs_path: str,
                 entity_tags: Optional[Dict[str, str]] = None,
                 caller_file_path: Optional[str] = None,
                 caller_file_line_range: Optional[Tuple[int, int]] = None,
                 bc_check_id: Optional[str] = None,
                 resource_address: Optional[str] = None,
                 severity: Optional[Severity] = None,
                 bc_category: Optional[str] = None,
                 benchmarks: dict[str, list[str]] | None = None,
                 description: Optional[str] = None,
                 short_description: Optional[str] = None,
                 vulnerability_details: Optional[Dict[str, Any]] = None,
                 connected_node: Optional[Dict[str, Any]] = None,
                 details: Optional[List[str]] = None,
                 check_len: int | None = None,
                 definition_context_file_path: Optional[str] = None,
                 validation_status: Optional[str] = None
                 ):
        super().__init__(check_id=check_id,
                         check_name=check_name,
                         check_result=check_result,
                         code_block=code_block,
                         file_path=file_path,
                         file_line_range=file_line_range,
                         resource=resource,
                         evaluations=evaluations,
                         check_class=check_class,
                         file_abs_path=file_abs_path,
                         entity_tags=entity_tags,
                         bc_check_id=bc_check_id,
                         severity=severity,
                         details=details,
                         caller_file_path=caller_file_path,
                         caller_file_line_range=caller_file_line_range,
                         resource_address=resource_address,
                         bc_category=bc_category,
                         benchmarks=benchmarks,
                         description=description,
                         short_description=short_description,
                         vulnerability_details=vulnerability_details,
                         connected_node=connected_node,
                         check_len=check_len,
                         definition_context_file_path=definition_context_file_path
                         )
        self.validation_status = validation_status
