from __future__ import annotations

from typing import Any

from checkov.common.output.record import Record


class GraphRecord(Record):
    def __init__(self, record: Record, breadcrumbs: dict[str, dict[str, Any]]):
        super().__init__(record.check_id, record.check_name, record.check_result, record.code_block, record.file_path,
                         record.file_line_range, record.resource, record.evaluations, record.check_class,
                         record.file_abs_path, record.entity_tags, record.caller_file_path,
                         record.caller_file_line_range, bc_check_id=record.bc_check_id, resource_address=record.resource_address,
                         severity=record.severity, bc_category=record.bc_category, benchmarks=record.benchmarks, details=record.details,
                         definition_context_file_path=record.definition_context_file_path)
        self.fixed_definition = record.fixed_definition
        self.breadcrumbs = breadcrumbs
