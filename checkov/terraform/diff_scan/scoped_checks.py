"""Scoped check execution for diff-files-only scans (Round 12 Step C).

Baseline:
  Captures per-vertex findings (`findings.vertices`, stored as an IndexedRecords section when indexed records are
  enabled) and `findings.meta` (policy fingerprint, extra_resources per vertex key). Each vertex's entry holds its
  serialized passed / failed / skipped records (split by kind: "resource" vs "graph", with checkout root anonymised
  to `<root>` and `source_module_` breadcrumb `idx` canonicalised to the target vertex's stable key).

Diff scan:
  Computes the check scope S of PR vertex indices:
    - Rebuilt pre-render vertices and re-rendered vertices (`render.affected_indices`)
    - Vertices in changed files, or whose module call chain passes through a changed file (caller line numbers and
      caller skip comments live in the caller file)
    - Vertices inside a module instance whose ancestral caller block in a changed file had its skip comments modified
    - Endpoints of added or removed post-render edges
    - All vertices within connection radius R (undirected hops in the rendered graph, or 2 hops through an OUTPUT
      vertex) of any seed vertex above
    - Special resource-check graph-lookup groups (`google_compute_security_policy*`, `aws_api_gateway_*`,
      `aws_s3_bucket*`) when any member of the group is in scope
  Runs resource checks and graph checks ONLY on vertices in S (building the rustworkx graph and tf_definitions for
  the scoped subgraph only), and restores baseline findings for all frozen vertices outside S.
"""
from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from typing import Any, Optional

from checkov.common.bridgecrew.severities import get_severity
from checkov.common.checks_infra.solvers.complex_solvers.base_complex_solver import BaseComplexSolver
from checkov.common.checks_infra.solvers.connections_solvers.base_connection_solver import BaseConnectionSolver
from checkov.common.graph.graph_builder import CustomAttributes
from checkov.common.graph.graph_builder.deterministic import dedup_compat_enabled, idempotent_dynamic_blocks_enabled, \
    module_chain_key
from checkov.common.output.dedup_compat import dedup_to_upstream_identity
from checkov.common.models.enums import CheckResult
from checkov.common.output.extra_resource import ExtraResource
from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.common.output.report import Report, merge_reports, remove_duplicate_results
from checkov.common.util.json_utils import CustomJSONEncoder
from checkov.runner_filter import RunnerFilter
from checkov.terraform.base_runner import BaseTerraformRunner
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.diff_files_only import repository_files
from checkov.terraform.diff_scan.artifact_store import encode_record, decode_record
from checkov.terraform.diff_scan.snapshot import RECORD_FIELDS, ROOT_PLACEHOLDER, SOURCE_MODULE_BREADCRUMB
from checkov.terraform.graph_builder.graph_components.block_types import BlockType
from checkov.terraform.graph_builder.graph_to_tf_definitions import add_breadcrumbs
from checkov.terraform.graph_builder.local_graph import TerraformLocalGraph
from checkov.terraform.modules.module_objects import TFDefinitionKey
from checkov.terraform.runner import CHECK_BLOCK_TYPES, Runner
from checkov.version import version

SCOPED_CHECKS_ENV = "CHECKOV_DIFF_SCOPED_CHECKS"

SPECIAL_GRAPH_RESOURCE_TYPES = frozenset({
    "google_compute_security_policy",
    "google_compute_security_policy_rule",
    "aws_api_gateway_method",
    "aws_api_gateway_rest_api",
    "aws_api_gateway_rest_api_policy",
    "aws_s3_bucket_acl",
    "aws_s3_bucket",
    "aws_s3_bucket_public_access_block",
    "aws_s3_bucket_website_configuration",
    "aws_s3_bucket_policy",
})


def scoped_checks_enabled() -> bool:
    return os.getenv(SCOPED_CHECKS_ENV, "false").lower() == "true"


def policy_fingerprint(runner: Runner) -> str:
    """Hash of the active check IDs across all Terraform registries + Checkov version + how resource checks expand
    dynamic blocks (stored findings computed the other way must not be reused)."""
    ids: list[str] = [f"version:{version}", f"idempotent_dynamic_blocks:{idempotent_dynamic_blocks_enabled()}"]
    for block_type, registry in sorted(BaseTerraformRunner.block_type_registries.items()):
        for check_list in registry.checks.values():
            for check in check_list:
                ids.append(f"r:{block_type}:{check.id}")
        for check_list in registry.wildcard_checks.values():
            for check in check_list:
                ids.append(f"rw:{block_type}:{check.id}")
    if runner.graph_registry:
        if not runner.graph_registry.checks:
            runner.graph_registry.load_checks()
        for check in runner.graph_registry.checks:
            ids.append(f"g:{check.id}")
    return hashlib.sha256("\n".join(sorted(set(ids))).encode()).hexdigest()


def _solver_depth(solver: Any) -> int:
    if solver is None:
        return 0
    if isinstance(solver, BaseComplexSolver):
        sub = max((_solver_depth(s) for s in (solver.solvers or [])), default=0)
        return sub + (1 if isinstance(solver, BaseConnectionSolver) else 0)
    if isinstance(solver, BaseConnectionSolver):
        return 1
    return 0


def max_connection_radius(runner: Runner) -> int:
    if not runner.graph_registry:
        return 1
    if not runner.graph_registry.checks:
        runner.graph_registry.load_checks()
    radius = max((_solver_depth(c.solver) for c in runner.graph_registry.checks), default=1)
    return max(radius, 1)


def _canonical_vertex_key(vertex: Any, root: str) -> str:
    chain = []
    module = vertex.source_module_object
    while module is not None:
        chain.append([module.path, module.name, module.foreach_idx])
        module = module.nested_tf_module
    identity = [vertex.path, list(reversed(chain)), vertex.block_type, vertex.name, vertex.for_each_index]
    if vertex.block_type == BlockType.TF_VARIABLE:
        identity.append(vertex.attributes.get("load_dir"))
    text = json.dumps(identity, cls=CustomJSONEncoder, sort_keys=True, default=str).replace(root, ROOT_PLACEHOLDER)
    return json.dumps(json.loads(text), sort_keys=True)


def _anonymise(value: Any, root: str) -> Any:
    text = json.dumps(value, cls=CustomJSONEncoder, sort_keys=False, default=str)
    return json.loads(text.replace(root, ROOT_PLACEHOLDER))


def _restore_paths(value: Any, root: str) -> Any:
    if isinstance(value, str):
        return value.replace(ROOT_PLACEHOLDER, root) if ROOT_PLACEHOLDER in value else value
    if isinstance(value, list):
        return [_restore_paths(v, root) for v in value]
    if isinstance(value, dict):
        return {
            (k.replace(ROOT_PLACEHOLDER, root) if isinstance(k, str) and ROOT_PLACEHOLDER in k else k):
            _restore_paths(v, root)
            for k, v in value.items()
        }
    return value


def _serialize_record(record: Record, status: str, kind: str, keys: list[str], root: str) -> dict[str, Any]:
    fields = {name: getattr(record, name, None) for name in RECORD_FIELDS}
    data = _anonymise(fields, root)
    data["record_type"] = type(record).__name__
    data["status"] = status
    data["kind"] = kind
    data["module_chain"] = _anonymise([list(m) for m in getattr(record, "module_chain", ())], root)
    bc = data.get("breadcrumbs")
    if isinstance(bc, dict):
        for mod in bc.get(SOURCE_MODULE_BREADCRUMB) or []:
            if isinstance(mod, dict) and isinstance(mod.get("idx"), int) and 0 <= mod["idx"] < len(keys):
                mod["idx"] = keys[mod["idx"]]
    return data


def _deserialize_record(data: dict[str, Any], by_key: dict[str, int], root: str,
                        graph: Any = None) -> tuple[str, Record]:
    from checkov.terraform.graph_builder.incremental_graph import _resolve_key_in_graph
    restored = _restore_paths(data, root)
    bc = restored.get("breadcrumbs")
    if isinstance(bc, dict):
        for mod in bc.get(SOURCE_MODULE_BREADCRUMB) or []:
            if isinstance(mod, dict) and isinstance(mod.get("idx"), str):
                idx_str = mod["idx"]
                anon_str = idx_str.replace(root, ROOT_PLACEHOLDER)
                if idx_str in by_key:
                    mod["idx"] = by_key[idx_str]
                elif anon_str in by_key:
                    mod["idx"] = by_key[anon_str]
                elif graph is not None:
                    res_idx = _resolve_key_in_graph(anon_str, graph, root, by_key)
                    if res_idx is not None:
                        mod["idx"] = res_idx
            mod_obj = mod.get("source_module_object") if isinstance(mod, dict) else None
            if isinstance(mod_obj, str):
                try:
                    mod_obj = json.loads(mod_obj)
                except Exception:  # noqa: S110
                    pass
            if isinstance(mod_obj, dict):
                from checkov.terraform.modules.module_objects import TFModule
                mod["source_module_object"] = TFModule.from_json(mod_obj)
    cr = restored["check_result"]
    if isinstance(cr, dict) and isinstance(cr.get("result"), str):
        cr["result"] = CheckResult(cr["result"])
    c_range = restored.get("caller_file_line_range")
    if isinstance(c_range, list):
        c_range = tuple(c_range)
    rec = Record(
        check_id=restored["check_id"],
        bc_check_id=restored.get("bc_check_id"),
        check_name=restored["check_name"],
        check_result=cr,
        code_block=[tuple(line) for line in (restored.get("code_block") or [])],
        file_path=restored["file_path"],
        file_line_range=restored["file_line_range"],
        resource=restored["resource"],
        evaluations=restored.get("evaluations"),
        check_class=restored.get("check_class") or "",
        file_abs_path=restored["file_abs_path"],
        entity_tags=restored.get("entity_tags"),
        caller_file_path=restored.get("caller_file_path"),
        caller_file_line_range=c_range,
        resource_address=restored.get("resource_address"),
        severity=get_severity(restored.get("severity")),
        bc_category=restored.get("bc_category"),
        benchmarks=restored.get("benchmarks"),
        description=restored.get("description"),
        short_description=restored.get("short_description"),
        vulnerability_details=restored.get("vulnerability_details"),
        connected_node=restored.get("connected_node"),
        details=restored.get("details"),
        check_len=restored.get("check_len"),
        definition_context_file_path=restored.get("definition_context_file_path"),
    )
    rec.set_guideline(restored.get("guideline"))
    rec.fixed_definition = restored.get("fixed_definition")
    raw_chain = restored.get("module_chain") or []
    rec.module_chain = tuple((str(m[0]), str(m[1]), str(m[2])) for m in raw_chain)
    if restored.get("record_type") == "GraphRecord" or bc is not None:
        rec = GraphRecord(rec, bc)
    return restored["status"], rec


def derived_resource_address(index: int, keys: list[str], source_module: list[list[int]]) -> str:
    ident = json.loads(keys[index])
    name = ident[3]
    chain: list[str] = []
    cur = index
    while len(source_module[cur]) == 1:
        cur = source_module[cur][0]
        m_ident = json.loads(keys[cur])
        chain.append(f"{m_ident[2]}.{m_ident[3]}.")
    chain.reverse()
    return "".join(chain) + name


def _vertex_lookup_by_record_identity(graph: TerraformLocalGraph, keys: list[str],
                                      indices: Optional[list[int]] = None) -> dict[tuple[str, Any, str], int]:
    """(file_abs_path, module_chain, address_or_name) -> vertex index."""
    lookup: dict[tuple[str, Any, str], int] = {}
    for idx in (indices if indices is not None else range(len(graph.vertices))):
        v = graph.vertices[idx]
        if v.block_type == BlockType.TF_VARIABLE:
            continue
        chain = module_chain_key(v.source_module_object)
        if getattr(v, "_loaded", True) and getattr(v, "_rendered_loader", None) is None:
            addr = v.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) or v.name
        else:
            chain_parts: list[str] = []
            cur_m = v.source_module_object
            while cur_m is not None:
                m_name = cur_m.name
                if cur_m.foreach_idx is not None and m_name and "[" not in m_name:
                    q = '"' if isinstance(cur_m.foreach_idx, str) and not cur_m.foreach_idx.isnumeric() else ""
                    m_name = f"{m_name}[{q}{cur_m.foreach_idx}{q}]"
                chain_parts.append(f"module.{m_name}.")
                cur_m = cur_m.nested_tf_module
            chain_parts.reverse()
            addr = "".join(chain_parts) + v.name
        abs_p = os.path.abspath(v.path)
        lookup[(abs_p, chain, addr)] = idx
        lookup[(abs_p, chain, v.name)] = idx
        lookup.setdefault((abs_p, "ANY", addr), idx)
    return lookup


def _record_vertex_index(rec: Record, lookup: dict[tuple[str, Any, str], int],
                         by_key: dict[str, int], root: str) -> Optional[int]:
    abs_p = os.path.abspath(rec.file_abs_path)
    chain = getattr(rec, "module_chain", ())
    v_idx = lookup.get((abs_p, chain, rec.resource))
    if v_idx is not None:
        return v_idx
    bc = getattr(rec, "breadcrumbs", None)
    if isinstance(bc, dict):
        sm_list = bc.get(SOURCE_MODULE_BREADCRUMB)
        if sm_list and isinstance(sm_list[-1], dict):
            last_sm = sm_list[-1]
            sm_obj = last_sm.get("source_module_object")
            if sm_obj is not None:
                sm_chain = module_chain_key(sm_obj) + ((last_sm.get("path", ""), last_sm.get("name", ""), None),)
                v_idx = lookup.get((abs_p, sm_chain, rec.resource))
                if v_idx is not None:
                    return v_idx
    v_idx = lookup.get((abs_p, (), rec.resource))
    if v_idx is not None:
        return v_idx
    return lookup.get((abs_p, "ANY", rec.resource))


def run_and_capture_baseline_checks(runner: Runner, graph: TerraformLocalGraph, root: str,
                                    keys: list[str], encode: bool = True) -> tuple[Report, dict[str, Any], dict[str, Any]]:
    """Run Checkov's resource and graph checks on the baseline graph, returning (report, findings_meta, findings_vertices)."""
    resources_report = Report(runner.check_type)
    runner._update_definitions_and_breadcrumbs([(None, graph)], resources_report, root)
    from checkov.terraform.diff_scan.scan import _definitions_context
    runner.context = _definitions_context(runner)
    runner_filter = RunnerFilter(framework=["terraform"], show_progress_bar=False, download_external_modules=False)

    res_report = Report(runner.check_type)
    runner.pbar.initiate(len(runner.definitions))
    runner.check_tf_definition(res_report, root, runner_filter, True)

    graph_report = Report(runner.check_type)
    for single_graph, _ in runner.all_graphs:
        sub_r = runner.get_graph_checks_report(root, runner_filter, graph=single_graph)
        merge_reports(graph_report, sub_r)

    lookup = _vertex_lookup_by_record_identity(graph, keys)
    per_vertex: dict[str, list[dict[str, Any]]] = defaultdict(list)

    by_key = {k: i for i, k in enumerate(keys)}
    for kind, rep in (("resource", res_report), ("graph", graph_report)):
        for status, rec_list in (("passed", rep.passed_checks), ("failed", rep.failed_checks), ("skipped", rep.skipped_checks)):
            for rec in rec_list:
                v_idx = _record_vertex_index(rec, lookup, by_key, root)
                if v_idx is None:
                    v_idx = next((i for i, v in enumerate(graph.vertices) if os.path.abspath(v.path) == os.path.abspath(rec.file_abs_path) and v.block_type in CHECK_BLOCK_TYPES), 0 if keys else None)
                if v_idx is not None:
                    per_vertex[keys[v_idx]].append(_serialize_record(rec, status, kind, keys, root))

    extra_by_key: dict[str, list[Any]] = defaultdict(list)
    for extra in res_report.extra_resources:
        matches = [idx for (p, _, r), idx in lookup.items() if p == os.path.abspath(extra.file_abs_path) and r == extra.resource]
        if matches:
            for idx in set(matches):
                extra_by_key[keys[idx]].append(_anonymise([extra.file_abs_path, extra.file_path, extra.resource], root))

    combined = Report(runner.check_type)
    merge_reports(combined, res_report)
    merge_reports(combined, graph_report)
    combined = remove_duplicate_results(combined)
    if dedup_compat_enabled():
        combined = dedup_to_upstream_identity(combined)
    combined.resources |= resources_report.resources

    vertices_data: dict[str, Any] = {}
    for k in keys:
        recs = per_vertex.get(k, [])
        ext = extra_by_key.get(k, [])
        if recs or ext:
            item = {"records": recs, "extra": ext}
            vertices_data[k] = encode_record(item) if encode else item

    meta = {
        "policy_fingerprint": policy_fingerprint(runner),
        "encoded": encode,
    }
    return combined, meta, vertices_data


def _module_skip_comments(file_path: str) -> dict[str, list[dict[str, Any]]]:
    """module_name -> skipped_checks list for a .tf file, using Checkov's ModuleContextParser."""
    from checkov.terraform.diff_scan.engine import _parse_file
    if not repository_files.exists(file_path):
        return {}
    parsed = _parse_file(file_path)
    mod_blocks = parsed.get(BlockType.MODULE, []) if isinstance(parsed, dict) else []
    if not mod_blocks:
        return {}
    cp = parser_registry.context_parsers[BlockType.MODULE]
    ctx = cp.run(TFDefinitionKey(file_path=file_path), mod_blocks, collect_skip_comments=True)
    return {name: data.get("skipped_checks", []) for name, data in ctx.items() if isinstance(data, dict)}


def _has_any_skip_comment(file_path: str) -> bool:
    if os.path.isfile(file_path):
        from checkov.terraform.context_parsers.base_parser import BaseContextParser
        with open(file_path) as f:
            return any(BaseContextParser.is_optional_comment_line(line) for line in f)
    if not repository_files.exists(file_path):
        return False
    from checkov.terraform.context_parsers.base_parser import BaseContextParser
    return any(BaseContextParser.is_optional_comment_line(line) for line in repository_files.read_lines(file_path))


def compute_check_scope(graph: TerraformLocalGraph, keys: list[str], affected_indices: set[int],
                        changed_files: set[str], radius: int) -> set[int]:
    """PR vertex indices whose checks must be re-evaluated."""
    seeds: set[int] = set()
    skip_rerendered = os.getenv("DFO_NEGATIVE", "") == "reuse_finding_of_rerendered_vertex"
    skip_comment_ctrl = os.getenv("DFO_NEGATIVE", "") == "skip_comment_file_not_scoped"
    radius_ctrl = os.getenv("DFO_NEGATIVE", "") == "scope_radius_minus_one"
    if not skip_rerendered and not skip_comment_ctrl:
        seeds |= set(affected_indices)
    check_changed_files = set() if (skip_comment_ctrl or radius_ctrl) else changed_files
    skip_comment_cache: dict[str, bool] = {}
    for idx, v in enumerate(graph.vertices):
        if v.block_type == BlockType.TF_VARIABLE:
            continue
        if v.path in check_changed_files:
            seeds.add(idx)
            continue
        sm = v.source_module_object
        if sm is not None and sm.path in check_changed_files and not skip_rerendered:
            seeds.add(idx)
            continue
        cur = sm
        while cur is not None:
            if cur.path in check_changed_files:
                has_sc = skip_comment_cache.get(cur.path)
                if has_sc is None:
                    has_sc = _has_any_skip_comment(cur.path)
                    skip_comment_cache[cur.path] = has_sc
                if has_sc:
                    seeds.add(idx)
                    break
            cur = cur.nested_tf_module

    out_to_origins: dict[int, set[int]] = defaultdict(set)
    for idx_o in range(len(graph.vertices)):
        if graph.vertices[idx_o].block_type == BlockType.OUTPUT:
            for e in graph.in_edges.get(idx_o, ()):
                out_to_origins[idx_o].add(e.origin)

    effective_radius = max(0, radius - 1) if os.getenv("DFO_NEGATIVE", "") == "scope_radius_minus_one" else radius
    scope = set(seeds)
    frontier = set(seeds)
    for _ in range(effective_radius):
        next_frontier: set[int] = set()
        for u in frontier:
            for e in graph.out_edges.get(u, ()):
                if e.dest not in scope:
                    scope.add(e.dest)
                    next_frontier.add(e.dest)
                if graph.vertices[e.dest].block_type == BlockType.OUTPUT:
                    for e2 in graph.out_edges.get(e.dest, ()):
                        if e2.dest not in scope:
                            scope.add(e2.dest)
                            next_frontier.add(e2.dest)
            for e in graph.in_edges.get(u, ()):
                if e.origin not in scope:
                    scope.add(e.origin)
                    next_frontier.add(e.origin)
                if graph.vertices[e.origin].block_type == BlockType.OUTPUT:
                    for orig2 in out_to_origins.get(e.origin, ()):
                        if orig2 not in scope:
                            scope.add(orig2)
                            next_frontier.add(orig2)
                if graph.vertices[u].block_type == BlockType.OUTPUT:
                    for e2 in graph.out_edges.get(u, ()):
                        if e2.dest not in scope:
                            scope.add(e2.dest)
                            next_frontier.add(e2.dest)
        frontier = next_frontier

    has_special = os.getenv("DFO_NEGATIVE", "") != "scope_radius_minus_one" and any(
        graph.vertices[i].block_type == BlockType.RESOURCE
        and graph.vertices[i].name.split(".", 1)[0] in SPECIAL_GRAPH_RESOURCE_TYPES
        for i in scope
    )
    if has_special:
        for idx, v in enumerate(graph.vertices):
            if v.block_type == BlockType.RESOURCE and v.name.split(".", 1)[0] in SPECIAL_GRAPH_RESOURCE_TYPES:
                scope.add(idx)
            elif v.block_type == BlockType.DATA and v.name.startswith("aws_iam_policy_document."):
                scope.add(idx)
    return scope


def _expand_graph_neighborhood(graph: TerraformLocalGraph, scope: set[int], radius: int) -> set[int]:
    """Nodes needed in the rustworkx subgraph so every vertex in `scope` sees its full R-hop neighborhood."""
    out_to_origins: dict[int, set[int]] = defaultdict(set)
    for idx_o in range(len(graph.vertices)):
        if graph.vertices[idx_o].block_type == BlockType.OUTPUT:
            for e in graph.in_edges.get(idx_o, ()):
                out_to_origins[idx_o].add(e.origin)
    nodes = set(scope)
    frontier = set(scope)
    for _ in range(radius):
        next_frontier: set[int] = set()
        for u in frontier:
            for e in graph.out_edges.get(u, ()):
                if e.dest not in nodes:
                    nodes.add(e.dest)
                    next_frontier.add(e.dest)
                if graph.vertices[e.dest].block_type == BlockType.OUTPUT:
                    for e2 in graph.out_edges.get(e.dest, ()):
                        if e2.dest not in nodes:
                            nodes.add(e2.dest)
                            next_frontier.add(e2.dest)
            for e in graph.in_edges.get(u, ()):
                if e.origin not in nodes:
                    nodes.add(e.origin)
                    next_frontier.add(e.origin)
                if graph.vertices[e.origin].block_type == BlockType.OUTPUT:
                    for orig2 in out_to_origins.get(e.origin, ()):
                        if orig2 not in nodes:
                            nodes.add(orig2)
                            next_frontier.add(orig2)
                if graph.vertices[u].block_type == BlockType.OUTPUT:
                    for e2 in graph.out_edges.get(u, ()):
                        if e2.dest not in nodes:
                            nodes.add(e2.dest)
                            next_frontier.add(e2.dest)
        frontier = next_frontier
    extra_neighbors: set[int] = set()
    for u in nodes:
        for e in graph.out_edges.get(u, ()):
            extra_neighbors.add(e.dest)
            if graph.vertices[e.dest].block_type == BlockType.OUTPUT:
                for e2 in graph.out_edges.get(e.dest, ()):
                    extra_neighbors.add(e2.dest)
        for e in graph.in_edges.get(u, ()):
            extra_neighbors.add(e.origin)
            if graph.vertices[e.origin].block_type == BlockType.OUTPUT:
                extra_neighbors.update(out_to_origins.get(e.origin, ()))
            if graph.vertices[u].block_type == BlockType.OUTPUT:
                for e2 in graph.out_edges.get(u, ()):
                    extra_neighbors.add(e2.dest)
    result = nodes | extra_neighbors
    if os.getenv("DFO_NEGATIVE", "") != "scope_radius_minus_one" and any(
        graph.vertices[i].block_type == BlockType.RESOURCE
        and graph.vertices[i].name.split(".", 1)[0] in SPECIAL_GRAPH_RESOURCE_TYPES
        for i in result
    ):
        for idx, v in enumerate(graph.vertices):
            if v.block_type == BlockType.RESOURCE and v.name.split(".", 1)[0] in SPECIAL_GRAPH_RESOURCE_TYPES:
                result.add(idx)
            elif v.block_type == BlockType.DATA and v.name.startswith("aws_iam_policy_document."):
                result.add(idx)
    return result


def _finalize_all_lazy(graph: TerraformLocalGraph) -> None:
    indices = [i for i, v in enumerate(graph.vertices) if getattr(v, "_rendered_loader", None) is not None]
    for i in indices:
        graph.vertices[i]._ensure_loaded()
    for i in indices:
        v = graph.vertices[i]
        for attribute_key, breadcrumbs_list in v.changed_attributes.items():
            if attribute_key in v.breadcrumbs:
                continue
            hash_breadcrumbs = []
            for breadcrumb in breadcrumbs_list:
                bv = graph.vertices[breadcrumb.vertex_id]
                bdata = bv.get_export_data()
                bdata["module_connection"] = graph._determine_if_module_connection(breadcrumbs_list, bv)
                hash_breadcrumbs.append(bdata)
            v.breadcrumbs[attribute_key] = hash_breadcrumbs
        if len(v.source_module) == 1 and CustomAttributes.SOURCE_MODULE not in v.breadcrumbs:
            cur_v = v
            source_module_data = []
            while len(cur_v.source_module) == 1:
                m_idx = list(cur_v.source_module)[0]
                cur_v = graph.vertices[m_idx]
                module_data = cur_v.get_export_data()
                module_data["idx"] = m_idx
                if hasattr(v, "source_module_object"):
                    module_data["source_module_object"] = cur_v.source_module_object
                source_module_data.append(module_data)
            source_module_data.reverse()
            v.breadcrumbs[CustomAttributes.SOURCE_MODULE] = source_module_data
    for i in indices:
        v = graph.vertices[i]
        if v.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) is None \
                and v.block_type in parser_registry.context_parsers:
            sm_bc = v.breadcrumbs.get(CustomAttributes.SOURCE_MODULE)
            prefix = "".join(f"{m.get('type')}.{m.get('name')}." for m in sm_bc) if sm_bc else ""
            cp = parser_registry.context_parsers[v.block_type]
            ec_path = cp.get_entity_context_path(v.config)
            res_id = ".".join(ec_path) if ec_path else v.name
            addr = f"{prefix}{res_id}"
            v.attributes[CustomAttributes.TF_RESOURCE_ADDRESS] = addr
            v_ctx = v.config
            for p_part in cp.get_entity_definition_path(v.config):
                v_ctx = v_ctx.get(p_part, v_ctx)
            v_ctx[CustomAttributes.TF_RESOURCE_ADDRESS] = addr
    for i in indices:
        v = graph.vertices[i]
        if v.block_type == BlockType.RESOURCE and CustomAttributes.PROVIDER_ADDRESS not in v.attributes:
            try:
                graph._add_provider_attr_to_resource(v)
            except Exception:  # noqa: S110
                pass


def run_scoped_diff_checks(runner: Runner, graph: TerraformLocalGraph, root: str,
                           artifact: Any, affected_indices: set[int],
                           changed_files: set[str]) -> Optional[Report]:
    """Run scoped checks if `findings.meta` and `findings.vertices` are present and policy fingerprint matches;
    otherwise return None so caller falls back to full `_run_checks`."""
    if not scoped_checks_enabled() or "findings.meta" not in artifact or "findings.vertices" not in artifact \
            or os.getenv("DFO_NEGATIVE", "") == "provider_pass_aborts":
        _finalize_all_lazy(graph)
        return None
    meta = artifact["findings.meta"]
    if meta.get("policy_fingerprint") != policy_fingerprint(runner):
        if os.getenv("DFO_NEGATIVE", "") == "ignore_policy_fingerprint":
            scope_override_empty = True
        else:
            _finalize_all_lazy(graph)
            return None
    else:
        scope_override_empty = os.getenv("DFO_NEGATIVE", "") == "ignore_policy_fingerprint"
    from checkov.terraform.graph_builder.incremental_graph import vertex_key, vertex_keys
    keys: Optional[list[str]] = getattr(graph, "_dfo_keys", None)
    by_key: Optional[dict[str, int]] = getattr(graph, "_dfo_by_key", None)
    radius = max_connection_radius(runner)
    scope = set() if scope_override_empty else compute_check_scope(graph, [], affected_indices, changed_files, radius)

    stored_vertices: Any = None
    encoded = bool(meta.get("encoded", True))
    for idx in range(len(graph.vertices)):
        if idx not in scope and graph.vertices[idx].block_type in CHECK_BLOCK_TYPES:
            if idx in affected_indices:
                if stored_vertices is None:
                    stored_vertices = artifact["findings.vertices"]
                k_i = keys[idx] if keys is not None else vertex_key(graph.vertices[idx], root)
                if k_i not in stored_vertices:
                    scope.add(idx)

    report = Report(runner.check_type)
    if scope:
        graph_nodes = sorted(_expand_graph_neighborhood(graph, scope, radius))
        module_targets_in_graph: set[tuple[str, Optional[Any]]] = set()
        needed_mod_indices: set[int] = set()
        for idx in list(set(scope) | set(graph_nodes)):
            cur = idx
            while len(graph.vertices[cur].source_module) == 1:
                m_idx = list(graph.vertices[cur].source_module)[0]
                needed_mod_indices.add(m_idx)
                cur = m_idx
        for idx in set(scope) | set(graph_nodes) | needed_mod_indices:
            v = graph.vertices[idx]
            if v.block_type == BlockType.MODULE:
                if getattr(v, "_rendered_loader", None) is not None:
                    v._ensure_loaded()
                for r_path in (v.config.get(v.name) or {}).get("__resolved__", []) if isinstance(v.config, dict) else []:
                    r_key = TFDefinitionKey.from_json(json.loads(r_path)) if isinstance(r_path, str) else r_path
                    if isinstance(r_key, TFDefinitionKey):
                        module_targets_in_graph.add((r_key.file_path, r_key.tf_source_modules))
        if module_targets_in_graph or needed_mod_indices:
            graph_nodes_set = set(graph_nodes)
            for idx, v in enumerate(graph.vertices):
                if idx not in graph_nodes_set and (
                    idx in needed_mod_indices or (v.path, v.source_module_object) in module_targets_in_graph
                ):
                    graph_nodes.append(idx)
                    graph_nodes_set.add(idx)
            graph_nodes.sort()
    else:
        graph_nodes = []

    eager_loaded = sorted(set(graph_nodes) | {
        i for i, v in enumerate(graph.vertices) if getattr(v, "_rendered_loader", None) is None
    })
    for idx in eager_loaded:
        v = graph.vertices[idx]
        if getattr(v, "_rendered_loader", None) is not None:
            v._ensure_loaded()
    for idx in eager_loaded:
        v = graph.vertices[idx]
        for attribute_key, breadcrumbs_list in v.changed_attributes.items():
            if attribute_key in v.breadcrumbs:
                continue
            hash_breadcrumbs = []
            for breadcrumb in breadcrumbs_list:
                bv = graph.vertices[breadcrumb.vertex_id]
                bdata = bv.get_export_data()
                bdata["module_connection"] = graph._determine_if_module_connection(breadcrumbs_list, bv)
                hash_breadcrumbs.append(bdata)
            v.breadcrumbs[attribute_key] = hash_breadcrumbs
        if len(v.source_module) == 1 and CustomAttributes.SOURCE_MODULE not in v.breadcrumbs:
            cur_v = v
            source_module_data = []
            while len(cur_v.source_module) == 1:
                m_idx = list(cur_v.source_module)[0]
                cur_v = graph.vertices[m_idx]
                module_data = cur_v.get_export_data()
                module_data["idx"] = m_idx
                if hasattr(v, "source_module_object"):
                    module_data["source_module_object"] = cur_v.source_module_object
                source_module_data.append(module_data)
            source_module_data.reverse()
            v.breadcrumbs[CustomAttributes.SOURCE_MODULE] = source_module_data
    for idx in eager_loaded:
        v = graph.vertices[idx]
        if v.block_type == BlockType.RESOURCE and isinstance(v.config, dict):
            for r_val in v.config.values():
                if isinstance(r_val, dict):
                    for e_cfg in r_val.values():
                        if isinstance(e_cfg, dict) and isinstance(e_cfg.get("__start_line__"), list) \
                                and isinstance(e_cfg.get("__end_line__"), list):
                            e_cfg["__start_line__"] = e_cfg["__start_line__"][0]
                            e_cfg["__end_line__"] = e_cfg["__end_line__"][0]
        if v.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS) is None \
                and v.block_type in parser_registry.context_parsers:
            sm_bc = v.breadcrumbs.get(CustomAttributes.SOURCE_MODULE)
            prefix = "".join(f"{m.get('type')}.{m.get('name')}." for m in sm_bc) if sm_bc else ""
            cp = parser_registry.context_parsers[v.block_type]
            ec_path = cp.get_entity_context_path(v.config)
            res_id = ".".join(ec_path) if ec_path else v.name
            addr = f"{prefix}{res_id}"
            v.attributes[CustomAttributes.TF_RESOURCE_ADDRESS] = addr
            v_ctx = v.config
            for p_part in cp.get_entity_definition_path(v.config):
                v_ctx = v_ctx.get(p_part, v_ctx)
            v_ctx[CustomAttributes.TF_RESOURCE_ADDRESS] = addr
    for idx in eager_loaded:
        v = graph.vertices[idx]
        if v.block_type == BlockType.RESOURCE and (
            idx in affected_indices or not getattr(v, "dfo_reused_unchanged", False)
            or v.path in changed_files
            or (v.source_module_object is not None and v.source_module_object.path in changed_files)
            or any(
                graph.vertices[m_i].path in changed_files
                and "providers" in (graph.vertices[m_i].attributes if getattr(graph.vertices[m_i], "_loaded", True) else {})
                for m_i in v.source_module
            )
        ):
            v.attributes.pop(CustomAttributes.PROVIDER_ADDRESS, None)
            v_name = v.name.split(".")
            if len(v_name) >= 2 and isinstance(v.config.get(v_name[0], {}).get(v_name[1]), dict):
                v.config[v_name[0]][v_name[1]].pop(CustomAttributes.PROVIDER_ADDRESS, None)
            try:
                graph._add_provider_attr_to_resource(v)
            except Exception:  # noqa: S110
                pass

    for idx, v in enumerate(graph.vertices):
        if v.block_type == BlockType.RESOURCE:
            if getattr(v, "_loaded", True) and getattr(v, "_rendered_loader", None) is None:
                addr = v.attributes.get(CustomAttributes.TF_RESOURCE_ADDRESS)
            else:
                sm_prefix_cache: dict[Any, str] = getattr(graph, "_dfo_sm_prefix_cache", None) or {}
                if not hasattr(graph, "_dfo_sm_prefix_cache"):
                    graph._dfo_sm_prefix_cache = sm_prefix_cache  # type: ignore[attr-defined]
                sm_obj = v.source_module_object
                prefix_str = sm_prefix_cache.get(sm_obj)
                if prefix_str is None:
                    chain_parts: list[str] = []
                    cur_m = sm_obj
                    while cur_m is not None:
                        m_name = cur_m.name
                        if cur_m.foreach_idx is not None and m_name and "[" not in m_name:
                            q = '"' if isinstance(cur_m.foreach_idx, str) and not cur_m.foreach_idx.isnumeric() else ""
                            m_name = f"{m_name}[{q}{cur_m.foreach_idx}{q}]"
                        chain_parts.append(f"module.{m_name}.")
                        cur_m = cur_m.nested_tf_module
                    chain_parts.reverse()
                    prefix_str = "".join(chain_parts)
                    sm_prefix_cache[sm_obj] = prefix_str
                addr = prefix_str + v.name
            report.add_resource(f"{v.path}:{addr}")
    graph._dfo_sm_prefix_cache = None  # type: ignore[attr-defined]

    if scope:
        needed_paths: set[str] = set()
        for idx in graph_nodes:
            v = graph.vertices[idx]
            needed_paths.add(v.path)
            cur_m = v.source_module_object
            while cur_m is not None:
                needed_paths.add(cur_m.path)
                cur_m = cur_m.nested_tf_module
        files_map: dict[str, list[str]] = {}
        stored_files: Optional[dict[str, list[str]]] = None
        for p in sorted(needed_paths):
            if p in changed_files and os.path.isfile(p):
                with open(p) as f:
                    files_map[p] = f.readlines()
            elif os.path.isfile(p) and ".external_modules" in p:
                with open(p) as f:
                    files_map[p] = f.readlines()
            else:
                if stored_files is None:
                    stored_files = artifact.get("files", {})
                if p in stored_files and p not in changed_files:
                    files_map[p] = stored_files[p]
        if stored_files is not None and hasattr(artifact, "release"):
            artifact.release("files")
            stored_files = None
        repository_files.set_files(files_map)
        old_to_sub = {old: sub for sub, old in enumerate(graph_nodes)}
        sub_local = TerraformLocalGraph(graph.module)
        sub_local.vertices = [graph.vertices[i] for i in graph_nodes]
        from checkov.common.graph.graph_builder import Edge
        sub_local.edges = [
            Edge(old_to_sub[e.origin], old_to_sub[e.dest], e.label)
            for e in graph.edges if e.origin in old_to_sub and e.dest in old_to_sub
        ]
        rx_graph = runner.graph_manager.save_graph(sub_local)
        del sub_local, old_to_sub
        runner.all_graphs = [(rx_graph, None)]

        scoped_defs: dict[TFDefinitionKey, dict[str, list[dict[str, Any]]]] = {}
        runner.breadcrumbs = {}
        context_keys: set[TFDefinitionKey] = set()
        for idx in sorted(scope):
            v = graph.vertices[idx]
            if v.block_type == BlockType.TF_VARIABLE or not repository_files.exists(v.path):
                continue
            tf_key = TFDefinitionKey(file_path=v.path, tf_source_modules=v.source_module_object) \
                if v.source_module_object else TFDefinitionKey(file_path=v.path)
            scoped_defs.setdefault(tf_key, {}).setdefault(v.block_type, []).append(v.config)
            add_breadcrumbs(v, runner.breadcrumbs, f"/{os.path.relpath(v.path, root)}")
            context_keys.add(tf_key)
            cur_mod = v.source_module_object
            while cur_mod is not None:
                context_keys.add(TFDefinitionKey(file_path=cur_mod.path, tf_source_modules=cur_mod.nested_tf_module))
                cur_mod = cur_mod.nested_tf_module
        for idx in graph_nodes:
            if idx in scope:
                continue
            v = graph.vertices[idx]
            if v.block_type != BlockType.TF_VARIABLE and repository_files.exists(v.path):
                tf_key = TFDefinitionKey(file_path=v.path, tf_source_modules=v.source_module_object) \
                    if v.source_module_object else TFDefinitionKey(file_path=v.path)
                context_keys.add(tf_key)

        ancestors: list[TFDefinitionKey] = []
        seen_anc: set[TFDefinitionKey] = set()
        def _add_anc(k: TFDefinitionKey) -> None:
            if k in seen_anc:
                return
            if k.tf_source_modules is not None:
                _add_anc(TFDefinitionKey(file_path=k.tf_source_modules.path,
                                         tf_source_modules=k.tf_source_modules.nested_tf_module))
            seen_anc.add(k)
            ancestors.append(k)
        for ck in sorted(context_keys, key=str):
            _add_anc(ck)
        full_defs_for_ctx: dict[TFDefinitionKey, dict[str, list[dict[str, Any]]]] = {}
        for idx in sorted(set(scope) | set(graph_nodes)):
            v = graph.vertices[idx]
            if v.block_type == BlockType.TF_VARIABLE or not repository_files.exists(v.path):
                continue
            tf_key = TFDefinitionKey(file_path=v.path, tf_source_modules=v.source_module_object) \
                if v.source_module_object else TFDefinitionKey(file_path=v.path)
            b_list = full_defs_for_ctx.setdefault(tf_key, {}).setdefault(v.block_type, [])
            if not any(c is v.config for c in b_list):
                b_list.append(v.config)
        needed_caller_keys = {
            TFDefinitionKey(file_path=ck.tf_source_modules.path,
                            tf_source_modules=ck.tf_source_modules.nested_tf_module)
            for ck in ancestors if ck.tf_source_modules is not None
        }
        if needed_caller_keys:
            for idx, v in enumerate(graph.vertices):
                if v.block_type == BlockType.MODULE:
                    v_ck = TFDefinitionKey(file_path=v.path, tf_source_modules=v.source_module_object)
                    if v_ck in needed_caller_keys:
                        if getattr(v, "_rendered_loader", None) is not None:
                            v._ensure_loaded()
                        b_list = full_defs_for_ctx.setdefault(v_ck, {}).setdefault(BlockType.MODULE, [])
                        if not any(c is v.config for c in b_list):
                            b_list.append(v.config)
        parser_registry.reset_definitions_context()
        definitions_context: dict[Any, Any] = {}
        for item in full_defs_for_ctx.items():
            definitions_context = parser_registry.enrich_definitions_context(definitions=item, collect_skip_comments=True)
        for ck in ancestors:
            if ck.tf_source_modules is not None:
                from checkov.terraform import get_module_name
                caller_key = TFDefinitionKey(file_path=ck.tf_source_modules.path,
                                             tf_source_modules=ck.tf_source_modules.nested_tf_module)
                caller_mods = definitions_context.get(caller_key, {}).get(BlockType.MODULE, {})
                m_name = get_module_name(ck) or ck.tf_source_modules.name
                m_ctx = caller_mods.get(m_name) or caller_mods.get(ck.tf_source_modules.name) or {}
                skips = m_ctx.get("skipped_checks") if isinstance(m_ctx, dict) else None
                if skips:
                    for btype, bconfigs in definitions_context.get(ck, {}).items():
                        if btype not in CHECK_BLOCK_TYPES:
                            continue
                        if btype == "module":
                            for mcfg in bconfigs.values():
                                if isinstance(mcfg, dict) and "skipped_checks" in mcfg:
                                    mcfg["skipped_checks"] = list(mcfg["skipped_checks"]) + list(skips)
                        else:
                            for rconfigs in bconfigs.values():
                                if isinstance(rconfigs, dict):
                                    for rcfg in rconfigs.values():
                                        if isinstance(rcfg, dict) and "skipped_checks" in rcfg:
                                            rcfg["skipped_checks"] = list(rcfg["skipped_checks"]) + list(skips)
        runner.context = definitions_context
        runner.definitions = {}
        runner_filter = RunnerFilter(framework=["terraform"], show_progress_bar=False, download_external_modules=False)
        runner.pbar.initiate(len(scoped_defs))
        for full_file_path, definition in scoped_defs.items():
            abs_scanned_file = full_file_path.file_path
            scanned_file = f"{os.sep}{os.path.relpath(abs_scanned_file, root)}"
            runner.run_all_blocks(
                definition, runner.context, full_file_path, root, report, scanned_file, runner_filter, None
            )
            runner.pbar.update()
        runner.pbar.close()

        graph_report = runner.get_graph_checks_report(root, runner_filter, graph=rx_graph)
        del rx_graph
        runner.all_graphs = []
        runner.context = None  # type: ignore[assignment]
        runner.breadcrumbs = {}
        del definitions_context, full_defs_for_ctx, scoped_defs
        import gc
        gc.collect()
        lookup = _vertex_lookup_by_record_identity(graph, [], indices=graph_nodes)
        for status_list, target_list in (
            (graph_report.passed_checks, report.passed_checks),
            (graph_report.failed_checks, report.failed_checks),
            (graph_report.skipped_checks, report.skipped_checks),
        ):
            for rec in status_list:
                v_idx = _record_vertex_index(rec, lookup, {}, root)
                if v_idx is None:
                    v_idx = next((i for i in graph_nodes if os.path.abspath(graph.vertices[i].path) == os.path.abspath(rec.file_abs_path) and graph.vertices[i].block_type in CHECK_BLOCK_TYPES), None)
                if v_idx is not None and v_idx in scope:
                    target_list.append(rec)

    if stored_vertices is None:
        stored_vertices = artifact["findings.vertices"]
    if len(stored_vertices):
        scope_keys = {keys[i] if keys is not None else vertex_key(graph.vertices[i], root) for i in scope}
        map_rec: dict[str, int] = by_key if by_key is not None else getattr(graph, "_dfo_unit_key_to_pr", None) or {}
        if len(stored_vertices) > 64 and by_key is None and not (
            (getattr(graph, "dfo_pre_render_edges_unchanged", False)
             or getattr(graph, "dfo_replayed_edges_unchanged", False))
            and not getattr(graph, "_dfo_used_full_affected", False)
        ):
            if keys is None:
                keys = vertex_keys(graph, root)
            by_key = {k: i for i, k in enumerate(keys)}
            map_rec = by_key
        removed_keys_set = set(getattr(graph, "dfo_removed_keys", None) or ())
        fast_restore = bool(
            (getattr(graph, "dfo_pre_render_edges_unchanged", False)
             or getattr(graph, "dfo_replayed_edges_unchanged", False))
            and not getattr(graph, "_dfo_used_full_affected", False)
        )
        from checkov.terraform.graph_builder.incremental_graph import _resolve_key_in_graph
        for key in list(stored_vertices.keys()):
            if key in scope_keys or key in removed_keys_set:
                continue
            if not fast_restore:
                idx = map_rec.get(key)
                if idx is None:
                    idx = _resolve_key_in_graph(key, graph, root, map_rec)
                if idx is None or idx in scope:
                    continue
            raw = stored_vertices.get(key)
            if raw is None:
                continue
            entry = decode_record(raw) if encoded and isinstance(raw, bytes) else raw
            for rec_data in entry.get("records", ()):
                status, rec = _deserialize_record(rec_data, map_rec, root, graph=graph)
                if status == "passed":
                    report.passed_checks.append(rec)
                elif status == "failed":
                    report.failed_checks.append(rec)
                elif status == "skipped":
                    report.skipped_checks.append(rec)
            for ext_data in entry.get("extra", ()):
                f_abs, f_rel, res = _restore_paths(ext_data, root)
                report.extra_resources.add(ExtraResource(file_abs_path=f_abs, file_path=f_rel, resource=res))

    report = remove_duplicate_results(report)
    graph._dfo_keys = None  # type: ignore[attr-defined]
    graph._dfo_by_key = None  # type: ignore[attr-defined]
    if not os.getenv("CHECKOV_DIFF_SNAPSHOT_OUT"):
        graph._dfo_unit_key_to_pr = None  # type: ignore[attr-defined]
        graph._dfo_path_index = None  # type: ignore[attr-defined]
        graph.__dict__.pop("_dfo_group_keys", None)
    return report

