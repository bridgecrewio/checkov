"""Compare two canonical scan snapshots (CHECKOV_DIFF_SNAPSHOT_OUT) for exact equality.

    python -m checkov.terraform.diff_scan.verify full_snapshot.json diff_snapshot.json

Compares every vertex attribute, every edge (with multiplicity), every finding field and status, resources and parsing
errors. Paths are anonymised to "<root>", so snapshots taken at different absolute roots compare equal. Exit 0 when
identical, 1 otherwise.
"""
from __future__ import annotations

import json
import sys
from collections import Counter

from checkov.terraform.diff_scan.compare import compare


def _status_counts(snapshot: dict) -> dict:
    return dict(Counter(record["status"] for record in snapshot["findings"].values()))


def main(argv: list[str]) -> int:
    expected_path, actual_path = argv
    with open(expected_path) as f:
        expected = json.load(f)
    with open(actual_path) as f:
        actual = json.load(f)
    result = compare(expected, actual)
    print(json.dumps({
        "identical": result["identical"],
        "graph_identical": result["graph_identical"],
        "findings_identical": result["findings_identical"],
        "vertices": {"expected": len(expected["graph"]["vertices"]), "actual": len(actual["graph"]["vertices"]),
                     "attribute_differences": result["vertices"]["attribute_differences"],
                     "missing": result["vertices"]["missing"], "extra": result["vertices"]["extra"]},
        "edges": {"expected": len(expected["graph"]["edges"]), "actual": len(actual["graph"]["edges"]),
                  "missing": result["edges"]["missing"], "extra": result["edges"]["extra"]},
        "findings": {"expected_by_status": _status_counts(expected), "actual_by_status": _status_counts(actual),
                     "false_negatives_FAILED": result["false_negatives_FAILED"],
                     "false_positives_FAILED": result["false_positives_FAILED"],
                     "missing": result["findings"]["missing"], "extra": result["findings"]["extra"]},
        "resources_identical": result["resources"]["equal"],
    }, indent=1))
    return 0 if result["identical"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
