"""Serialize Checkov records to the metadata graph and back, independently of the checkout path.

Every field downstream consumers read is persisted (CAS reads check_id, check_name, check_result,
code_block, file_path, file_abs_path, file_line_range, resource, entity_tags, connected_node, severity,
details, guideline, caller info). `file_abs_path` is stored repo-relative and re-anchored on load.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from checkov.common.models.enums import CheckResult
from checkov.common.output.record import Record
from checkov.common.output.report import Report


def _rel(root: str, path: Any) -> Any:
    if isinstance(path, str) and os.path.isabs(path):
        return os.path.relpath(path, root)
    return path


def _abs(root: str, path: Any) -> Any:
    if isinstance(path, str) and path and not os.path.isabs(path):
        return os.path.join(root, path)
    return path


def _json_safe(value: Any) -> Any:
    return json.loads(json.dumps(value, default=str))


def record_to_json(root: str, record: Record) -> dict[str, Any]:
    result = dict(record.check_result)
    result["result"] = result["result"].name if isinstance(result.get("result"), CheckResult) else result.get("result")
    result.pop("entity", None)  # full entity config can be large and may contain rendered secrets
    return _json_safe({
        "check_id": record.check_id,
        "bc_check_id": record.bc_check_id,
        "check_name": record.check_name,
        "check_result": result,
        "code_block": record.code_block,
        "file_path": record.file_path,
        "file_abs_path": _rel(root, record.file_abs_path),
        "file_line_range": record.file_line_range,
        "resource": record.resource,
        "evaluations": record.evaluations,
        "entity_tags": record.entity_tags,
        "caller_file_path": record.caller_file_path,
        "caller_file_line_range": record.caller_file_line_range,
        "resource_address": record.resource_address,
        "severity": record.severity.name if record.severity is not None and hasattr(record.severity, "name")
        else record.severity,
        "guideline": record.guideline,
        "details": record.details,
        "connected_node": record.connected_node,
        "definition_context_file_path": _rel(root, record.definition_context_file_path),
        "module_chain": [[_rel(root, path), name, idx] for path, name, idx in getattr(record, "module_chain", ())],
    })


def record_from_json(root: str, data: dict[str, Any]) -> Record:
    check_result = dict(data["check_result"])
    check_result["result"] = CheckResult[check_result["result"]]
    from checkov.common.bridgecrew.severities import get_severity
    severity = get_severity(data.get("severity"))
    record = Record(
        check_id=data["check_id"], bc_check_id=data["bc_check_id"], check_name=data["check_name"],
        check_result=check_result, code_block=[tuple(x) for x in data["code_block"]],
        file_path=data["file_path"], file_line_range=data["file_line_range"], resource=data["resource"],
        evaluations=data["evaluations"], check_class="", file_abs_path=_abs(root, data["file_abs_path"]),
        entity_tags=data["entity_tags"], caller_file_path=data["caller_file_path"],
        caller_file_line_range=data["caller_file_line_range"], resource_address=data["resource_address"],
        severity=severity, details=data["details"], connected_node=data["connected_node"],
        definition_context_file_path=_abs(root, data["definition_context_file_path"]),
    )
    record.module_chain = tuple((_abs(root, path), name, idx) for path, name, idx in data.get("module_chain", []))
    record.set_guideline(data["guideline"])
    return record


def report_to_json(root: str, report: Report) -> list[dict[str, Any]]:
    records = report.failed_checks + report.passed_checks + report.skipped_checks
    return sorted((record_to_json(root, r) for r in records), key=lambda d: json.dumps(d, sort_keys=True))


def records_to_report(root: str, check_type: str, records: list[dict[str, Any]]) -> Report:
    report = Report(check_type)
    for data in records:
        report.add_record(record_from_json(root, data))
    return report


def canonical_key(data: dict[str, Any]) -> tuple[Any, ...]:
    """Path-independent identity used to compare an incremental result with a full scan."""
    code = hashlib.sha256(json.dumps(data["code_block"], default=str).encode()).hexdigest()[:16]
    return (data["check_result"]["result"], data["check_id"], data["file_path"], tuple(data["file_line_range"]),
            str(data["resource"]), json.dumps(data.get("module_chain", [])), code)
