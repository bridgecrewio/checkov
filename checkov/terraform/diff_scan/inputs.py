"""Scan-input validation for diff-files-only PR scans: the diff must be exactly the baseline -> scan-target-tree diff.

A diff scan reuses everything the baseline derived from files the diff does not list, so it is only correct when
  (a) the baseline was taken at commit B and the caller's diff starts at B (not at some other commit),
  (b) every file that differs between B and the scan target tree is in the diff, with the target tree's content,
  (c) nothing else that changes Checkov's result changed (configuration, CLI options, Checkov itself).
Variable inputs outside the repository (--var-file, TF_VAR_*) are compared and recomputed by the diff engine itself.

The caller (Data Collector) supplies, for the scan target tree T (PR HEAD or a merge result, the caller's choice):
  base_commit      B: the commit the diff starts at
  target_tree_id   T's git tree / commit id (recorded in the report; identifies what was scanned)
  manifest         EVERY file of T: repository-relative path -> git blob SHA (`git ls-tree -r T`)
  changes          changed (added / modified) and deleted paths, with the content of the changed ones

The baseline records B, the blob SHA of every file of B (same manifest format) and a configuration fingerprint.
Validation runs BEFORE any changed file is parsed; a failure is an IncrementalGraphUnsupported with a reason code,
which the CLI turns into exit code 3 (the caller then runs a full scan).

File relevance (from Checkov's Terraform directory scan, verified by an audit of every file a full scan opens):
  graph inputs     .tf, .hcl, .tfvars, .tfvars.json (terraform.tfvars, *.auto.tfvars, --var-file targets)
  config inputs    .checkov.yml / .checkov.yaml (Checkov's CLI reads them from the scanned directory)
  never read       everything else, including .tf.json (handle_variables: "TODO: add support for .tf.json"),
                   files under directories Checkov skips (hidden directories, node_modules, .terraform, .serverless)
A file whose relevance cannot be decided this way does not exist: every path is classified by suffix and location.
Directory structure (added / removed / renamed folders) is covered because every file of T is in the manifest.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Optional

from checkov.terraform.graph_builder.incremental_graph import IncrementalGraphUnsupported

GRAPH_INPUT_SUFFIXES = (".tf", ".hcl", ".tfvars", ".tfvars.json")
CONFIG_FILE_NAMES = (".checkov.yml", ".checkov.yaml")
SKIPPED_DIRECTORY_NAMES = frozenset({"node_modules", ".terraform", ".serverless"})
"""Checkov's default CKV_IGNORED_DIRECTORIES; hidden directories are skipped too (CKV_IGNORE_HIDDEN_DIRECTORIES)."""

BASELINE_COMMIT_MISMATCH = "baseline_commit_mismatch"
INCOMPLETE_DIFF = "incomplete_diff"
CONTENT_MISMATCH = "content_mismatch"
CONFIG_MISMATCH = "config_mismatch"
MISSING_VALIDATION_INPUTS = "missing_validation_inputs"
REASON_CODES = (BASELINE_COMMIT_MISMATCH, INCOMPLETE_DIFF, CONTENT_MISMATCH, CONFIG_MISMATCH,
                MISSING_VALIDATION_INPUTS)


class InputValidationError(IncrementalGraphUnsupported):
    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason


def git_blob_sha(content: bytes) -> str:
    """The id git gives a file with this content (`git hash-object`)."""
    return hashlib.sha1(b"blob %d\0" % len(content) + content, usedforsecurity=False).hexdigest()


def _in_skipped_directory(path: str) -> bool:
    directories = path.split("/")[:-1]
    return any(d in SKIPPED_DIRECTORY_NAMES or d.startswith(".") for d in directories)


def is_graph_input(path: str) -> bool:
    return path.endswith(GRAPH_INPUT_SUFFIXES) and not _in_skipped_directory(path)


def is_config_input(path: str) -> bool:
    return path in CONFIG_FILE_NAMES


def is_relevant(path: str) -> bool:
    """Whether a repository-relative path ('/'-separated) can change the result of a Terraform scan."""
    return is_graph_input(path) or is_config_input(path)


def tree_manifest(root: str) -> dict[str, str]:
    """path -> git blob SHA for every file under `root` (what `git ls-tree -r` lists for a checkout; the baseline
    records it for B). The pre-scan's materialised external modules are not repository files."""
    from checkov.terraform.diff_scan.scanner_inputs import MATERIALIZED_DIR

    manifest: dict[str, str] = {}
    for directory, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not (directory == root and d == MATERIALIZED_DIR) and d != ".git")
        for name in names:
            path = os.path.join(directory, name)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            with open(path, "rb") as f:
                manifest[os.path.relpath(path, root).replace(os.sep, "/")] = git_blob_sha(f.read())
    return manifest


RESULT_SETTINGS = ("framework", "skip_framework", "check", "skip_check", "skip_path", "external_checks_dir",
                   "external_checks_git", "run_all_external_checks", "include_all_checkov_policies",
                   "download_external_modules", "evaluate_variables", "deep_analysis", "skip_resources_without_violations")
"""Checkov CLI settings that change which findings a Terraform scan reports (resolved values: CLI flags, environment
and every config file Checkov loaded). Variable inputs (--var-file, TF_VAR_*) are not here: the diff engine compares
them with the baseline's and recomputes what they feed."""
RESULT_ENV_PREFIXES = ("CKV_", "CHECKOV_ENABLE_", "CHECKOV_EXPERIMENTAL_", "CHECKOV_MAX_", "CHECKOV_RENDER_",
                       "CHECKOV_GRAPH_FRAMEWORK", "RENDER_")
"""Checkov environment settings that can change graph construction or findings (ignored directories, for_each
handling, file size limits, render limits, ...). The PoC's own opt-in flags are set identically by every scan mode."""


def result_settings(config: Any) -> dict[str, Any]:
    """The RESULT_SETTINGS of a resolved Checkov configuration, with the content of external check directories."""
    settings = {name: getattr(config, name, None) for name in RESULT_SETTINGS}
    for directory in getattr(config, "external_checks_dir", None) or []:
        settings[f"external_checks_dir:{directory}"] = tree_manifest(directory) if os.path.isdir(directory) else None
    return settings


def config_fingerprint(settings: dict[str, Any]) -> str:
    """Everything outside the repository's Terraform files that changes a scan result: Checkov's version, the
    resolved result settings (which already include whatever a repository .checkov.yml set: Checkov's CLI loads it
    into the configuration) and the result-relevant environment."""
    from checkov.version import version as checkov_version

    payload = {"checkov": checkov_version, "python": list(sys.version_info[:2]), "settings": settings,
               "environment": {k: v for k, v in sorted(os.environ.items()) if k.startswith(RESULT_ENV_PREFIXES)}}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


@dataclass
class ScanTarget:
    base_commit: str
    target_tree_id: str
    manifest: dict[str, str]
    """every file of the scan target tree: repository-relative path -> git blob SHA"""


@dataclass
class BaselineInputs:
    commit: str
    manifest: dict[str, str]
    config_fingerprint: str

    def to_json(self) -> dict[str, Any]:
        return {"commit": self.commit, "manifest": self.manifest, "config_fingerprint": self.config_fingerprint}

    @staticmethod
    def from_json(data: Optional[dict[str, Any]]) -> Optional["BaselineInputs"]:
        if not data:
            return None
        return BaselineInputs(data["commit"], data["manifest"], data["config_fingerprint"])


@dataclass
class ValidationReport:
    base_commit: str = ""
    target_tree_id: str = ""
    files_in_target: int = 0
    relevant_changed: list[str] = field(default_factory=list)
    relevant_deleted: list[str] = field(default_factory=list)
    irrelevant_changes: int = 0


def validate(baseline: Optional[BaselineInputs], target: Optional[ScanTarget], changed: dict[str, bytes],
             deleted: list[str], fingerprint: str) -> ValidationReport:
    """Raises InputValidationError unless `changed` (path -> supplied content) and `deleted` are exactly the
    baseline -> scan-target-tree diff of every relevant file, and nothing else that affects the scan changed.
    Paths are repository-relative, '/'-separated."""
    if baseline is None or target is None:
        raise InputValidationError(MISSING_VALIDATION_INPUTS,
                                   "the baseline artifact or the scan request lacks commit / manifest data")
    if target.base_commit != baseline.commit:
        raise InputValidationError(BASELINE_COMMIT_MISMATCH,
                                   f"the diff starts at {target.base_commit}, the baseline was taken at "
                                   f"{baseline.commit}")
    if fingerprint != baseline.config_fingerprint:
        raise InputValidationError(CONFIG_MISMATCH, "Checkov version, scan settings, TF_VAR_* environment or the "
                                                    "repository's Checkov config file differ from the baseline's")
    _check_supplied_content(target.manifest, changed)
    _check_complete(baseline.manifest, target.manifest, set(changed), set(deleted))
    relevant_changed = sorted(p for p in changed if is_relevant(p))
    relevant_deleted = sorted(p for p in deleted if is_relevant(p))
    return ValidationReport(base_commit=target.base_commit, target_tree_id=target.target_tree_id,
                            files_in_target=len(target.manifest), relevant_changed=relevant_changed,
                            relevant_deleted=relevant_deleted,
                            irrelevant_changes=len(changed) + len(deleted) - len(relevant_changed)
                            - len(relevant_deleted))


def _check_supplied_content(target_manifest: dict[str, str], changed: dict[str, bytes]) -> None:
    for path, content in sorted(changed.items()):
        expected = target_manifest.get(path)
        if expected is None:
            raise InputValidationError(INCOMPLETE_DIFF, f"{path} is listed as changed but is not in the scan target "
                                                        f"tree's manifest")
        if git_blob_sha(content) != expected:
            raise InputValidationError(CONTENT_MISMATCH, f"supplied content of {path} is not the scan target tree's "
                                                         f"(blob {expected})")


def _check_complete(base: dict[str, str], target: dict[str, str], changed: set[str], deleted: set[str]) -> None:
    """Every relevant path whose blob differs between B and T is listed: as changed when it is in T, as deleted when
    it is not. A path listed as deleted must be absent from T. Irrelevant files need not be listed."""
    for path in sorted(deleted):
        if path in target:
            raise InputValidationError(INCOMPLETE_DIFF, f"{path} is listed as deleted but is in the scan target tree")
    for path in sorted(set(base) | set(target)):
        if not is_relevant(path) or base.get(path) == target.get(path):
            continue
        if path in target and path not in changed:
            raise InputValidationError(INCOMPLETE_DIFF, f"{path} differs from the baseline commit but is not in the "
                                                        f"diff")
        if path not in target and path not in deleted:
            raise InputValidationError(INCOMPLETE_DIFF, f"{path} was removed since the baseline commit but is not "
                                                        f"listed as deleted")
