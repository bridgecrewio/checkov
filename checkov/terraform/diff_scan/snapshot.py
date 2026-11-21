"""Checkout-independent snapshots of a Checkov Terraform scan, used to compare two scans for equality.

A snapshot has three parts:

  graph      every vertex of the Terraform graph with its full attribute dict (Block.get_attribute_dict, the
             same dict Checkov stores in its graph DB and CAS turns into assets), plus every edge.
  findings   every passed / failed / skipped record with ALL fields Checkov sets.
  resources  report.resources and report.extra_resources (the resource inventory).

Canonicalisation (the only transformations applied; everything else is compared verbatim):
  * absolute paths under the scanned root become "<root>" (two checkouts of one tree compare equal)
  * vertex list indices become stable vertex keys (file, module chain, block type, name, for_each index):
      - vertices and edge endpoints are keyed this way
      - breadcrumbs `source_module_[].idx` (Checkov stores the module vertex's list index) is replaced by the key
        of the vertex it points to, so it is still verified, but independently of how many other vertices exist
  * `check_result.evaluated_keys` of graph checks is sorted (Checkov builds it from a set; order is random)
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from checkov.common.output.record import Record
from checkov.common.output.report import Report
from checkov.common.util.json_utils import CustomJSONEncoder

ROOT_PLACEHOLDER = "<root>"
SOURCE_MODULE_BREADCRUMB = "source_module_"
RECORD_FIELDS = (
    "check_id", "bc_check_id", "check_name", "check_result", "code_block", "file_path", "file_abs_path",
    "file_line_range", "resource", "evaluations", "check_class", "entity_tags",
    "caller_file_path", "caller_file_line_range", "resource_address", "severity", "bc_category", "benchmarks",
    "description", "short_description", "vulnerability_details", "connected_node", "guideline", "details",
    "check_len", "definition_context_file_path", "breadcrumbs", "fixed_definition",
)
"""Every attribute Record / GraphRecord set, except:
  * `module_chain`: fork-only (set in deterministic mode), not part of stock Checkov's output
  * `repo_file_path`: os.path.relpath(file_abs_path) against the process CWD, not the scanned root, so it encodes
    where the scanner process runs from (CAS sets file paths from `file_path`, which is compared)"""


def to_json_safe(value: Any, root: str) -> Any:
    """JSON round trip through Checkov's own encoder, with the checkout root anonymised."""
    text = json.dumps(value, cls=CustomJSONEncoder, sort_keys=True, default=str)
    return json.loads(text.replace(root, ROOT_PLACEHOLDER))


def record_key(data: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def extra_resource_entry(resource: Any, root: str) -> str:
    return json.dumps(to_json_safe([resource.file_abs_path, resource.file_path, resource.resource,
                                    resource.file_line_range], root))


def disambiguate(keys: list[str], vertices: list[Any]) -> list[str]:
    """Invalid Terraform can declare the same address twice (Checkov keeps both blocks). Colliding keys get the
    block's line range appended, which is stable for the same file content."""
    seen: dict[str, int] = {}
    for key in keys:
        seen[key] = seen.get(key, 0) + 1
    return [key if seen[key] == 1 else
            f"{key}@{vertex.attributes.get('__start_line__')}-{vertex.attributes.get('__end_line__')}"
            for key, vertex in zip(keys, vertices)]


class Canonicalizer:
    """Canonical form of one scan. Built from the graph the scan's records were evaluated against."""

    def __init__(self, graph: Any, root: str) -> None:
        self.root = root
        self.keys = disambiguate([self.vertex_key(v) for v in graph.vertices], graph.vertices)
        if len(set(self.keys)) != len(self.keys):
            raise ValueError("vertex identity is not unique")
        self.graph = graph

    def vertex_key(self, vertex: Any) -> str:
        chain = []
        module = vertex.source_module_object
        while module is not None:
            chain.append([module.path, module.name, module.foreach_idx])
            module = module.nested_tf_module
        identity = [vertex.path, list(reversed(chain)), vertex.block_type, vertex.name, vertex.for_each_index]
        if vertex.block_type == "tfvar":
            # TF_VAR_* env vars create one vertex per directory, all with path "env:TF_VAR_<name>"
            identity.append(vertex.attributes.get("load_dir"))
        return json.dumps(to_json_safe(identity, self.root), sort_keys=True)

    def snapshot_graph(self) -> dict[str, Any]:
        vertices = {}
        for key, vertex in zip(self.keys, self.graph.vertices):
            attributes = to_json_safe(vertex.get_attribute_dict(add_hash=False), self.root)
            self._stable_breadcrumbs(attributes.get("rendering_breadcrumbs_"))
            vertices[key] = attributes
        edges = sorted(json.dumps([self.keys[e.origin], self.keys[e.dest], e.label]) for e in self.graph.edges)
        return {"vertices": vertices, "edges": edges}

    def snapshot_record(self, record: Record) -> dict[str, Any]:
        data = to_json_safe({name: getattr(record, name, None) for name in RECORD_FIELDS}, self.root)
        data["record_type"] = type(record).__name__
        self._stable_breadcrumbs(data["breadcrumbs"])
        evaluated_keys = data["check_result"].get("evaluated_keys")
        if isinstance(evaluated_keys, list):
            data["check_result"]["evaluated_keys"] = sorted(evaluated_keys, key=str)
        return data

    def snapshot_report(self, report: Report) -> dict[str, Any]:
        findings = {}
        for status, record in iter_records(report):
            data = self.snapshot_record(record)
            data["status"] = status
            findings[record_key(data)] = data
        return {
            "findings": findings,
            "resources": sorted(to_json_safe(sorted(report.resources), self.root)),
            "extra_resources": sorted(extra_resource_entry(r, self.root) for r in report.extra_resources),
            "parsing_errors": sorted(to_json_safe(sorted(report.parsing_errors), self.root)),
        }

    def _stable_breadcrumbs(self, breadcrumbs: Any) -> None:
        if not isinstance(breadcrumbs, dict):
            return
        for module in breadcrumbs.get(SOURCE_MODULE_BREADCRUMB) or []:
            if isinstance(module, dict) and isinstance(module.get("idx"), int):
                module["idx"] = self.keys[module["idx"]]


def iter_records(report: Report) -> list[tuple[str, Record]]:
    return [(status, record) for status, records in (("passed", report.passed_checks),
                                                     ("failed", report.failed_checks),
                                                     ("skipped", report.skipped_checks)) for record in records]


def snapshot_scan(graph: Any, report: Report, root: str) -> dict[str, Any]:
    canonical = Canonicalizer(graph, root)
    return {"graph": canonical.snapshot_graph(), **canonical.snapshot_report(report)}
