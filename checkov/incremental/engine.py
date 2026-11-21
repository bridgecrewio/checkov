"""Periodic metadata generation and PR-diff scanning.

    periodic:  metadata = generate_metadata(repo, frameworks)        # full scan, unit by unit
    PR:        report   = scan_diff(repo, metadata, changed_files)   # only the diff + the metadata

PR algorithm (per framework):
  1. dirty units  = units whose persisted file set contains a changed file (reverse index file_owners)
                    + units whose external module identity is not reusable (mutable ref, newly available)
  2. new files    = changed files that belong to no persisted unit. Units are re-discovered ONLY for those
                    files' framework, and any unit that contains a new file is dirty. This catches added
                    files and files whose role changed (e.g. a new Kubernetes manifest that now links
                    two previously independent components).
  3. graph re-link (Kubernetes): a changed manifest may link to / unlink from manifests that did not
                    change. Units are re-discovered from the current tree and every current unit that
                    shares a file with a dirty or new unit is also dirty.
  4. rescan dirty units with the stock runner, restricted to the union of their files (scope.only_files)
  5. merge: findings of dirty/removed units are replaced, all other units keep their persisted findings

Deleted files: a deleted file is a changed file; its unit is dirty and rescanned without it; a unit whose
files are all gone is dropped.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from checkov.common.graph.graph_builder.deterministic import DETERMINISTIC_GRAPH_ENV
from checkov.common.output.report import Report
from checkov.incremental import frameworks
from checkov.incremental.metadata import FrameworkMetadata, MetadataGraph, UnitMetadata, file_sha256
from checkov.incremental.records import records_to_report, report_to_json
from checkov.incremental.scope import only_files
from checkov.runner_filter import RunnerFilter
from checkov.version import version as checkov_version

SUPPORTED_FRAMEWORKS = ("terraform", "kubernetes", "cloudformation", "arm", "bicep", "dockerfile", "serverless",
                        "openapi", "github_actions", "ansible", "helm", "kustomize")
GRAPH_LINKED_FRAMEWORKS = {"kubernetes", "bicep", "helm", "kustomize"}

ExternalModuleProvider = Callable[[str, set[str]], dict[str, Any]]
"""(repo, unit_files) -> external_modules_content_cache for Terraform; mirrors the production module flow."""


def runner_for(framework: str) -> Any:
    module = {
        "terraform": "checkov.terraform.runner", "kubernetes": "checkov.kubernetes.runner",
        "cloudformation": "checkov.cloudformation.runner", "arm": "checkov.arm.runner",
        "bicep": "checkov.bicep.runner", "dockerfile": "checkov.dockerfile.runner",
        "serverless": "checkov.serverless.runner", "openapi": "checkov.openapi.runner",
        "github_actions": "checkov.github_actions.runner", "ansible": "checkov.ansible.runner",
        "helm": "checkov.helm.runner", "kustomize": "checkov.kustomize.runner",
    }[framework]
    return __import__(module, fromlist=["Runner"]).Runner()


def fingerprint(frameworks_: list[str], runner_filter: Optional[RunnerFilter], external_checks_hash: str) -> dict[str, Any]:
    rf = runner_filter or RunnerFilter()
    return {
        "checkov_version": checkov_version,
        "deterministic_graph": os.getenv(DETERMINISTIC_GRAPH_ENV, "false"),
        "frameworks": sorted(frameworks_),
        "checks": sorted(rf.checks or []),
        "skip_checks": sorted(rf.skip_checks or []),
        "external_checks_hash": external_checks_hash,
    }


@dataclass
class DiffScanResult:
    reports: dict[str, Report]
    metadata: MetadataGraph
    mode: str
    seconds: float
    units_rescanned: dict[str, list[str]] = field(default_factory=dict)
    units_reused: dict[str, int] = field(default_factory=dict)
    units_removed: dict[str, list[str]] = field(default_factory=dict)
    reasons: dict[str, dict[str, str]] = field(default_factory=dict)


class IncrementalScanner:
    def __init__(self, frameworks_: list[str], runner_filter: Optional[RunnerFilter] = None,
                 external_checks_dir: Optional[list[str]] = None,
                 external_module_provider: Optional[ExternalModuleProvider] = None,
                 external_checks_hash: str = "") -> None:
        unknown = set(frameworks_) - set(SUPPORTED_FRAMEWORKS)
        if unknown:
            raise ValueError(f"unsupported frameworks for incremental scanning: {sorted(unknown)}")
        os.environ[DETERMINISTIC_GRAPH_ENV] = "true"
        self.frameworks = list(frameworks_)
        self.runner_filter = runner_filter
        self.external_checks_dir = external_checks_dir
        self.external_module_provider = external_module_provider
        self.fingerprint = fingerprint(self.frameworks, runner_filter, external_checks_hash)

    # ------------------------------------------------------------------------------------------ scans

    def _filter(self, framework: str) -> RunnerFilter:
        rf = RunnerFilter(framework=[framework], show_progress_bar=False,
                          checks=self.runner_filter.checks if self.runner_filter else None,
                          skip_checks=self.runner_filter.skip_checks if self.runner_filter else None)
        rf.download_external_modules = False
        return rf

    def _external_cache(self, framework: str, root: str, files: set[str]) -> Optional[dict[str, Any]]:
        if framework != "terraform" or self.external_module_provider is None:
            return None
        return self.external_module_provider(root, files)

    def _scan_files(self, framework: str, root: str, files: set[str]) -> tuple[Report, dict[str, str]]:
        """Run the stock runner over `root`, restricted to `files`. Returns (report, external module ids)."""
        cache = self._external_cache(framework, root, files)
        runner = runner_for(framework)
        materialized = _materialized_module_files(root, cache)
        with only_files(root, files | materialized):
            if framework == "terraform" and cache is not None:
                result = self._run_terraform_with_modules(runner, root, framework, cache)
            else:
                result = runner.run(root_folder=root, external_checks_dir=self.external_checks_dir,
                                    runner_filter=self._filter(framework))
        reports = result if isinstance(result, list) else [result]
        report = next((r for r in reports if r.check_type == framework), reports[0] if reports else Report(framework))
        modules = _external_module_ids(runner, cache) if framework == "terraform" else {}
        return report, modules

    def _run_terraform_with_modules(self, runner: Any, root: str, framework: str, cache: dict[str, Any]) -> Any:
        from checkov.terraform.module_loading.registry import module_loader_registry

        previous = dict(module_loader_registry.module_content_cache)
        module_loader_registry.module_content_cache = dict(cache)
        graph, _ = runner.graph_manager.build_graph_from_source_directory(
            source_dir=root, external_modules_content_cache=cache, download_external_modules=False)
        runner._update_definitions_and_breadcrumbs([(None, graph)], Report(framework), root)
        from checkov.terraform.context_parsers.registry import parser_registry
        context: dict[str, Any] = {}
        for item in runner.definitions.items():
            context = parser_registry.enrich_definitions_context(definitions=item, collect_skip_comments=True)
        runner.context = context
        try:
            return runner.run(root_folder=root, external_checks_dir=self.external_checks_dir,
                              runner_filter=self._filter(framework))
        finally:
            module_loader_registry.module_content_cache = previous

    def _scan_unit(self, framework: str, root: str, unit_files: set[str]) -> UnitMetadata:
        report, modules = self._scan_files(framework, root, unit_files)
        return UnitMetadata(files=frameworks.hash_files(root, unit_files), records=report_to_json(root, report),
                            external_modules=modules)

    def _discover(self, framework: str, root: str) -> frameworks.UnitFiles:
        """Unit discovery never materializes external modules: which repository dirs are root modules, and
        which repository files each root module reaches, cannot depend on external module content
        (relative sources inside an external module resolve inside that module's own tree). Modules are
        fetched later, only for the units that are actually scanned."""
        return frameworks.discover_units(framework, root)

    # --------------------------------------------------------------------------------------- periodic

    def generate_metadata(self, repo: str) -> MetadataGraph:
        root = os.path.abspath(repo)
        metadata = MetadataGraph(fingerprint=self.fingerprint)
        for framework in self.frameworks:
            fw = FrameworkMetadata()
            for unit_id, files in sorted(self._discover(framework, root).items()):
                fw.units[unit_id] = self._scan_unit(framework, root, files)
            metadata.frameworks[framework] = fw
        return metadata

    # --------------------------------------------------------------------------------------------- PR

    def scan_diff(self, repo: str, baseline: Optional[MetadataGraph], changed_files: list[str]) -> DiffScanResult:
        started = time.perf_counter()
        root = os.path.abspath(repo)
        if baseline is None or baseline.fingerprint != self.fingerprint:
            metadata = self.generate_metadata(root)
            return DiffScanResult(reports=self._reports(root, metadata), metadata=metadata,
                                  mode="full (no baseline / fingerprint changed)",
                                  seconds=time.perf_counter() - started)

        changed = {os.path.normpath(f) for f in changed_files}
        result = DiffScanResult(reports={}, metadata=MetadataGraph(fingerprint=self.fingerprint), mode="diff",
                                seconds=0.0)
        for framework in self.frameworks:
            fw_old = baseline.frameworks.get(framework, FrameworkMetadata())
            fw_new, rescanned, removed, reasons = self._diff_framework(framework, root, fw_old, changed)
            result.metadata.frameworks[framework] = fw_new
            result.units_rescanned[framework] = rescanned
            result.units_removed[framework] = removed
            result.units_reused[framework] = len(fw_new.units) - len(rescanned)
            result.reasons[framework] = reasons
        result.reports = self._reports(root, result.metadata)
        result.seconds = time.perf_counter() - started
        return result

    def _diff_framework(self, framework: str, root: str, old: FrameworkMetadata, changed: set[str]
                        ) -> tuple[FrameworkMetadata, list[str], list[str], dict[str, str]]:
        owners = old.file_owners()
        reasons: dict[str, str] = {}
        for path in sorted(changed):
            for unit_id in owners.get(path, []):
                reasons.setdefault(unit_id, f"changed file {path}")
        for unit_id, unit in old.units.items():
            reason = _external_module_reason(unit, self.external_module_provider)
            if reason:
                reasons.setdefault(unit_id, reason)

        unowned = {p for p in changed if p not in owners and os.path.exists(os.path.join(root, p))}
        needs_discovery = bool(unowned) or (framework in GRAPH_LINKED_FRAMEWORKS and bool(reasons)) or \
            framework == "terraform" and bool(reasons)
        if not reasons and not unowned:
            return FrameworkMetadata(units=dict(old.units)), [], [], {}

        current = self._discover(framework, root) if needs_discovery else {
            uid: set(u.files) for uid, u in old.units.items()}
        dirty_files = {f for uid in reasons for f in old.units[uid].files} | unowned | changed
        new_units: dict[str, UnitMetadata] = {}
        rescanned: list[str] = []
        for unit_id, files in sorted(current.items()):
            previous = old.units.get(unit_id)
            if previous is None:
                reason = "new unit"
            elif set(files) != set(previous.files):
                reason = reasons.get(unit_id, "unit file set changed")
            elif files & dirty_files:
                reason = reasons.get(unit_id, "shares a file with a changed unit")
            else:
                reason = reasons.get(unit_id)
            if reason is None:
                new_units[unit_id] = previous  # type: ignore[assignment]
                continue
            new_units[unit_id] = self._scan_unit(framework, root, files)
            rescanned.append(unit_id)
            reasons[unit_id] = reason
        removed = sorted(set(old.units) - set(new_units))
        for unit_id in removed:
            reasons[unit_id] = "unit removed"
        kept_reasons = {k: v for k, v in reasons.items() if k in rescanned or k in removed}
        return FrameworkMetadata(units=new_units), rescanned, removed, kept_reasons

    @staticmethod
    def _reports(root: str, metadata: MetadataGraph) -> dict[str, Report]:
        reports: dict[str, Report] = {}
        for framework, fw in metadata.frameworks.items():
            records = [r for unit in fw.units.values() for r in unit.records]
            reports[framework] = _dedupe(records_to_report(root, framework, records))
        return reports


def _dedupe(report: Report) -> Report:
    from checkov.common.output.report import remove_duplicate_results
    return remove_duplicate_results(report)


# ------------------------------------------------------------------------------------------ external modules

IMMUTABLE_REF_SUFFIXES = ("v", "")


def is_immutable_ref(version: str) -> bool:
    import re
    return bool(re.fullmatch(r"v?\d+\.\d+\.\d+([-+][\w.]+)?|[0-9a-f]{40}", version or ""))


def _materialized_module_files(root: str, cache: Optional[dict[str, Any]]) -> set[str]:
    files: set[str] = set()
    for content in (cache or {}).values():
        path = content.path() if content is not None and content.loaded() else None
        if not path or os.path.commonpath([root, os.path.abspath(path)]) != root:
            continue
        for current, _, names in os.walk(path):
            files |= {os.path.relpath(os.path.join(current, n), root) for n in names}
    return files


def _external_module_ids(runner: Any, cache: Optional[dict[str, Any]]) -> dict[str, str]:
    from checkov.terraform.module_loading.module_finder import should_download

    ids: dict[str, str] = {}
    parser = runner.graph_manager.parser
    loaded = {f"{s}:{v}" for (s, v) in getattr(parser, "external_modules_source_map", {}) if should_download(s)}
    requested: set[str] = set()
    for definition in (runner.definitions or {}).values():
        for module_block in definition.get("module", []) or []:
            for _, conf in module_block.items():
                source = (conf.get("source") or [None])[0]
                if isinstance(source, str) and should_download(source):
                    version = (conf.get("version") or ["latest"])[0]
                    requested.add(f"{source}:{version}")
    for address in sorted(requested | loaded):
        version = address.rsplit(":", 1)[-1]
        if address not in loaded:
            ids[address] = "missing"
        elif is_immutable_ref(version):
            ids[address] = f"ref:{address}"
        else:
            content = (cache or {}).get(address)
            from checkov.incremental.metadata import tree_sha256
            ids[address] = "mutable:" + (tree_sha256(content.path()) if content else "?")
    return ids


def _external_module_reason(unit: UnitMetadata, provider: Optional[ExternalModuleProvider]) -> Optional[str]:
    mutable = sorted(a for a, i in unit.external_modules.items() if i.startswith("mutable:"))
    if mutable:
        return f"external module with mutable ref {mutable}"
    missing = sorted(a for a, i in unit.external_modules.items() if i == "missing")
    if missing and provider is not None and getattr(provider, "is_available", None):
        now = [a for a in missing if provider.is_available(a)]  # type: ignore[attr-defined]
        if now:
            return f"external module now available {now}"
    return None


def changed_files_from_hashes(root: str, baseline: MetadataGraph) -> list[str]:
    """Helper for callers without a git diff: compare current file hashes with the baseline's."""
    root = os.path.abspath(root)
    known = {f: h for fw in baseline.frameworks.values() for u in fw.units.values() for f, h in u.files.items()}
    return sorted(f for f, h in known.items() if file_sha256(os.path.join(root, f)) != h)
