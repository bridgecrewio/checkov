"""Output-only compatibility with upstream's record identity (CHECKOV_DEDUP_COMPAT).

Deterministic mode identifies a record by (check, file, line range, resource, module call chain), so a module
called from several root modules yields one record per instance. Upstream's identity has no module chain:
remove_duplicate_results keeps one record per (check, file, line range, resource), the one inserted last.

Which instance does upstream keep? Upstream checks Terraform definitions in vertex order, and for module code shared
by several callers its vertex order follows the module call chain (outer caller file, then module name, then index).
Measured on gcp-configuration (11,212 upstream records, 5,723 multi-instance groups): the instance upstream keeps
is the one with the greatest module chain in every group. Its breadcrumbs, entity_tags, caller_file and
check_result.entity are that instance's own, so every field matches except what the deterministic engine itself
computes differently (see REPORT.md: breadcrumb accumulation and evaluated_keys order).

This module keeps the record with the greatest module chain per upstream identity and drops the others. Records
keep their module_chain field (it is empty in upstream's output for every record; consumers comparing with upstream
should ignore it)."""
from __future__ import annotations

from typing import Any

from checkov.common.output.record import Record
from checkov.common.output.report import Report


def upstream_identity(record: Record) -> str:
    return f"{record.check_id}.{record.file_abs_path}.{record.file_line_range}.{record.resource}"


def _keep_greatest_module_chain(records: list[Record]) -> list[Record]:
    kept: dict[str, Record] = {}
    for record in records:
        identity = upstream_identity(record)
        current = kept.get(identity)
        if current is None or record.module_chain > current.module_chain:
            kept[identity] = record
    return list(kept.values())


def dedup_to_upstream_identity(report: Report) -> Report:
    """The same report object, with passed / failed records reduced to upstream's identity. Skipped records are left
    as they are: upstream's remove_duplicate_results does not deduplicate them either (one per module instance)."""
    report.passed_checks = _keep_greatest_module_chain(report.passed_checks)
    report.failed_checks = _keep_greatest_module_chain(report.failed_checks)
    return report


def dedup_reports(reports: Any) -> Any:
    """A Report, or a list of Reports (Checkov's runners may return either)."""
    if isinstance(reports, list):
        return [dedup_reports(r) for r in reports]
    if isinstance(reports, Report):
        return dedup_to_upstream_identity(reports)
    return reports
