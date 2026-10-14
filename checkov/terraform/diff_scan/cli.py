"""Diff-files-only Terraform scanning from the Checkov CLI (opt-in; nothing here runs without these flags).

Baseline (full scan of a checkout, writes the artifact):

    checkov -d <repo> --framework terraform --diff-baseline-out artifact.json [--external-modules-dir <dir>]
            [--var-file <f> ...] -o json

Reference full scan with exactly the same flags (the oracle a PR scan must equal):

    checkov -d <repo> --framework terraform --diff-full-scan [--external-modules-dir <dir>] -o json

PR scan (NO repository checkout needed: only the changed files are present in <payload_dir>):

    checkov -d <payload_dir> --framework terraform --diff-baseline artifact.json --diff-changes changes.json
            [--external-modules-dir <dir>] [--var-file <f> ...] [--diff-report report.json] -o json

changes.json (file-operation metadata, repository-relative paths):
    {"changed": ["app/main.tf", ...],          # added or modified: content MUST be present under <payload_dir>
     "deleted": ["app/old.tf", ...],           # removed (renames / moves = delete + add)
     "renamed": [{"from": "a.tf", "to": "b.tf"}]}  # optional sugar, expanded to delete + change

--external-modules-dir: the pre-scan's resolved external modules, ALL of them, every scan. Layout
    <dir>/manifest.txt                       one "<source>@<version>" per line
    <dir>/_sources/<slug(source)>/<version>/ module content
  materialised at <root>/.external_modules/ (production layout) before the scan.

Fail-closed contract: a listed changed file that is absent, a listed deleted file that is present, an external
module the baseline used that is missing, a --var-file with no content, a changed file that does not parse, or any
case the engine cannot place exactly -> exit code 3 with the reason on stderr; no findings are printed.
"""
from __future__ import annotations

import dataclasses
import json
import os
import sys
from typing import Any

UNSUPPORTED_EXIT_CODE = 3


def _changes(payload_dir: str, path: str) -> Any:
    from checkov.terraform.diff_scan.engine import ChangeSet

    with open(path) as f:
        raw = json.load(f)
    unknown = set(raw) - {"changed", "deleted", "renamed"}
    if unknown:
        raise ValueError(f"unknown keys in {path}: {sorted(unknown)}")
    changed = list(raw.get("changed", []))
    deleted = list(raw.get("deleted", []))
    for rename in raw.get("renamed", []):
        deleted.append(rename["from"])
        changed.append(rename["to"])
    root = os.path.realpath(payload_dir)
    for rel in changed + deleted:
        if os.path.isabs(rel) or rel.startswith(".."):
            raise ValueError(f"change paths must be repository-relative: {rel}")
    return ChangeSet(changed=sorted(os.path.join(root, p) for p in set(changed)),
                     deleted=sorted(os.path.join(root, p) for p in set(deleted)))


def _configure_inputs(config: Any, root: str) -> None:
    from checkov.terraform.diff_scan import scanner_inputs

    if getattr(config, "external_modules_dir", None):
        os.environ[scanner_inputs.MODULE_STORE_ENV] = os.path.abspath(config.external_modules_dir)
    var_files = [os.path.relpath(os.path.abspath(v), root) for v in (config.var_file or [])]
    if var_files:
        os.environ[scanner_inputs.VAR_FILES_ENV] = ",".join(var_files)


SNAPSHOT_ENV = "CHECKOV_DIFF_SNAPSHOT_OUT"
"""Test hook: also write a canonical snapshot (every vertex attribute, edges, every finding field) to this file, for
exact comparison against a full scan. Set by the PoC harness / DEMO_GUIDE verifier; never needed for normal use."""


def _write_snapshot(graph: Any, report: Any, root: str) -> None:
    path = os.getenv(SNAPSHOT_ENV)
    if not path:
        return
    from checkov.terraform.diff_scan.snapshot import snapshot_scan

    with open(path, "w") as f:
        json.dump(snapshot_scan(graph, report, root), f)


def _print_report(config: Any, report: Any) -> None:
    from checkov.common.util.json_utils import CustomJSONEncoder

    if "json" in (config.output or []):
        print(json.dumps(report.get_dict(is_quiet=config.quiet), indent=4, cls=CustomJSONEncoder))
    else:
        report.print_console(is_quiet=config.quiet, is_compact=config.compact)


def run_diff_scan(config: Any) -> int:
    from checkov.terraform.diff_scan import scan
    from checkov.terraform.graph_builder.incremental_graph import IncrementalGraphUnsupported

    if not config.directory or len(config.directory) != 1:
        raise SystemExit("diff-files-only scanning requires exactly one -d/--directory")
    root = os.path.realpath(config.directory[0])
    _configure_inputs(config, root)
    if config.diff_full_scan:
        result = scan.full_scan(root)
    elif config.diff_baseline_out:
        result = scan.baseline_scan(root)
        with open(config.diff_baseline_out, "w") as f:
            json.dump(result.artifact, f)
        print(f"[diff-scan] baseline artifact written: {config.diff_baseline_out} "
              f"({len(result.artifact['keys'])} pre-render vertices)", file=sys.stderr)
    else:
        if not config.diff_changes:
            raise SystemExit("--diff-baseline requires --diff-changes (file-operation metadata)")
        with open(config.diff_baseline) as f:
            artifact = json.load(f)
        try:
            result = scan.diff_scan(root, artifact, _changes(root, config.diff_changes))
        except (IncrementalGraphUnsupported, ValueError) as error:
            print(f"[diff-scan] UNSUPPORTED (no partial scan was run): {error}", file=sys.stderr)
            return UNSUPPORTED_EXIT_CODE
        summary = {"pre_render": dataclasses.asdict(result.pre_render), "render": dataclasses.asdict(result.render)}
        if config.diff_report:
            with open(config.diff_report, "w") as f:
                json.dump(summary, f, indent=1, default=str)
        p, r = result.pre_render, result.render
        print(f"[diff-scan] pre-render vertices rebuilt {p.vertices_rebuilt}/{p.vertices} reused {p.vertices_reused}; "
              f"edges rebuilt {p.edges_rebuilt}/{p.edges} reused {p.edges_reused}; units mode={p.mode} "
              f"spliced={p.units_reused}/{p.units_total} touched={ {k: v.get('mode') for k, v in p.scoped_units.items()} }; "
              f"rendered {r.affected}/{r.vertices} (frozen {r.frozen})", file=sys.stderr)
    _write_snapshot(result.graph, result.report, root)
    _print_report(config, result.report)
    failed = len(result.report.failed_checks)
    return 1 if failed and not config.soft_fail else 0
