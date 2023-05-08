from typing import List, Tuple, Optional, Dict, Any

from checkov.common.bridgecrew.severities import Severity
from checkov.common.output.record import Record
from checkov.common.typing import _CheckResult
from checkov.terraform.output.origin_module_metadata import OriginModuleMetadata


class TerraformRecord(Record):
    def __init__(
        self,
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
        origin_modules_metadata: Optional[List[OriginModuleMetadata]] = None
    ) -> None:
        super().__init__(check_id, check_name, check_result, code_block, file_path, file_line_range, resource,
                         evaluations, check_class, file_abs_path, entity_tags, caller_file_path, caller_file_line_range,
                         bc_check_id, resource_address, severity, bc_category, benchmarks, description,
                         short_description, vulnerability_details, connected_node, details, check_len,
                         definition_context_file_path)
        self.origin_modules_metadata = origin_modules_metadata or []

    @classmethod
    def from_reduced_json(cls, record_json: dict[str, Any]) -> "TerraformRecord":
        record = super().from_reduced_json(record_json)
        record.origin_modules_metadata = record_json['origin_modules_metadata']


