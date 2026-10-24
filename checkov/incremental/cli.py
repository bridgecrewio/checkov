"""CLI entry for incremental scanning.

    checkov -d repo --framework terraform kubernetes --incremental-metadata-out meta.json
    checkov -d repo --framework terraform kubernetes --incremental-baseline meta.json \
            --changed-files envs/prod/main.tf,k8s/app.yaml [--incremental-metadata-out new-meta.json] -o json
"""
from __future__ import annotations

import json
import os
from typing import Any

from checkov.incremental.engine import SUPPORTED_FRAMEWORKS, IncrementalScanner
from checkov.incremental.metadata import MetadataGraph, tree_sha256
from checkov.runner_filter import RunnerFilter


def run_incremental(config: Any) -> int:
    if not config.directory or len(config.directory) != 1:
        raise SystemExit("incremental scanning requires exactly one -d/--directory")
    repo = config.directory[0]
    frameworks = [f for f in (config.framework or ["all"]) if f != "all"] or list(SUPPORTED_FRAMEWORKS)
    external_checks_hash = "".join(tree_sha256(d) for d in (config.external_checks_dir or []))
    scanner = IncrementalScanner(
        frameworks,
        runner_filter=RunnerFilter(checks=config.check, skip_checks=config.skip_check),
        external_checks_dir=config.external_checks_dir,
        external_checks_hash=external_checks_hash,
    )
    if config.incremental_baseline:
        changed = [f.strip() for f in (config.changed_files or "").split(",") if f.strip()]
        result = scanner.scan_diff(repo, MetadataGraph.load(config.incremental_baseline), changed)
        metadata, reports = result.metadata, result.reports
        summary = {"mode": result.mode, "seconds": round(result.seconds, 3),
                   "units_rescanned": result.units_rescanned, "units_reused": result.units_reused,
                   "units_removed": result.units_removed, "reasons": result.reasons}
    else:
        metadata = scanner.generate_metadata(repo)
        reports = scanner._reports(os.path.abspath(repo), metadata)
        summary = {"mode": "periodic", "units": {f: len(fw.units) for f, fw in metadata.frameworks.items()}}
    if config.incremental_metadata_out:
        metadata.save(config.incremental_metadata_out)
    failed = sum(len(r.failed_checks) for r in reports.values())
    print(json.dumps({"incremental": summary,
                      "results": {f: r.get_summary() for f, r in reports.items()}}, indent=1, default=str))
    return 1 if failed and not config.soft_fail else 0
