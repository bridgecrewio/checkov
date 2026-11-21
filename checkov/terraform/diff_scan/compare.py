"""Compare two scan snapshots: graph (vertices with all attributes, edges), findings (all record fields),
resources, extra resources and parsing errors. Missing FAILED findings (false negatives) are counted apart."""
from __future__ import annotations

import json
from collections import Counter
from typing import Any

EXAMPLES = 3


def compare(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    vertices = _compare_vertices(expected["graph"]["vertices"], actual["graph"]["vertices"])
    edges = _compare_multisets(expected["graph"]["edges"], actual["graph"]["edges"])
    findings = _compare_findings(expected["findings"], actual["findings"])
    resources = _compare_sets(expected["resources"], actual["resources"])
    extra = _compare_sets(expected["extra_resources"], actual["extra_resources"])
    errors = _compare_sets(expected["parsing_errors"], actual["parsing_errors"])
    parts = {"vertices": vertices, "edges": edges, "findings": findings, "resources": resources,
             "extra_resources": extra, "parsing_errors": errors}
    return {
        "identical": all(p["equal"] for p in parts.values()),
        "graph_identical": vertices["equal"] and edges["equal"],
        "findings_identical": findings["equal"],
        "false_negatives_FAILED": findings["missing_FAILED"],
        "false_positives_FAILED": findings["extra_FAILED"],
        **parts,
    }


def _compare_sets(expected: list[str], actual: list[str]) -> dict[str, Any]:
    missing, extra = sorted(set(expected) - set(actual)), sorted(set(actual) - set(expected))
    return {"equal": not missing and not extra, "expected": len(set(expected)), "missing": len(missing),
            "extra": len(extra), "missing_examples": missing[:EXAMPLES], "extra_examples": extra[:EXAMPLES]}


def _compare_multisets(expected: list[str], actual: list[str]) -> dict[str, Any]:
    """Checkov keeps parallel edges (same endpoints and label), so edges are compared with multiplicity."""
    missing = sorted((Counter(expected) - Counter(actual)).elements())
    extra = sorted((Counter(actual) - Counter(expected)).elements())
    return {"equal": not missing and not extra, "expected": len(expected), "missing": len(missing),
            "extra": len(extra), "missing_examples": missing[:EXAMPLES], "extra_examples": extra[:EXAMPLES]}


def _compare_vertices(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    result = _compare_sets(list(expected), list(actual))
    changed = sorted(k for k in set(expected) & set(actual) if expected[k] != actual[k])
    result["attribute_differences"] = len(changed)
    result["equal"] = result["equal"] and not changed
    result["attribute_examples"] = [_attribute_diff(k, expected[k], actual[k]) for k in changed[:EXAMPLES]]
    return result


def _attribute_diff(key: str, expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    names = sorted(n for n in set(expected) | set(actual) if expected.get(n) != actual.get(n))
    return {"vertex": key, "attributes": {n: {"expected": _short(expected.get(n)), "actual": _short(actual.get(n))}
                                          for n in names[:5]}}


def _compare_findings(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    result = _compare_sets(list(expected), list(actual))
    missing = [expected[k] for k in set(expected) - set(actual)]
    extra = [actual[k] for k in set(actual) - set(expected)]
    result["missing_FAILED"] = sum(1 for r in missing if r["status"] == "failed")
    result["extra_FAILED"] = sum(1 for r in extra if r["status"] == "failed")
    result["missing_by_status"] = dict(Counter(r["status"] for r in missing))
    result["extra_by_status"] = dict(Counter(r["status"] for r in extra))
    result["missing_examples"] = [_finding_summary(r) for r in sorted(missing, key=_finding_order)[:EXAMPLES]]
    result["extra_examples"] = [_finding_summary(r) for r in sorted(extra, key=_finding_order)[:EXAMPLES]]
    return result


def _finding_order(record: dict[str, Any]) -> str:
    return json.dumps([record["status"], record["check_id"], record["file_path"], record["resource"]])


def _finding_summary(record: dict[str, Any]) -> list[Any]:
    return [record["status"], record["check_id"], record["file_path"], record["resource"], record["file_line_range"]]


def _short(value: Any) -> str:
    text = json.dumps(value, sort_keys=True, default=str)
    return text if len(text) <= 160 else text[:157] + "..."


def differences_by_unit(expected: dict[str, Any], actual: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Which root module (unit) each differing vertex / finding belongs to."""
    location_unit = _location_units(expected) | _location_units(actual)
    by_unit: dict[str, Counter] = {}

    def count(unit: str, kind: str) -> None:
        by_unit.setdefault(unit, Counter())[kind] += 1

    ve, va = expected["graph"]["vertices"], actual["graph"]["vertices"]
    for key in set(ve) ^ set(va) | {k for k in set(ve) & set(va) if ve[k] != va[k]}:
        count(_vertex_unit(key), "vertices")
    fe, fa = expected["findings"], actual["findings"]
    for key in set(fe) ^ set(fa):
        record = fe.get(key) or fa[key]
        count(location_unit.get((record["file_abs_path"], record["resource"]), "<unknown>"), "findings")
    return {unit: dict(counts) for unit, counts in sorted(by_unit.items())}


def _vertex_unit(key: str) -> str:
    identity = key if key.endswith("]") else key.rsplit("@", 1)[0]  # see canonical.disambiguate
    path, chain, *_ = json.loads(identity)
    origin = chain[0][0] if chain else path
    return origin.rsplit("/", 1)[0].replace("<root>/", "")


def _location_units(snapshot: dict[str, Any]) -> dict[tuple[str, str], str]:
    return {(attributes.get("file_path_"), attributes.get("__address__") or attributes.get("id_")): _vertex_unit(key)
            for key, attributes in snapshot["graph"]["vertices"].items()}


def finding_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, int]:
    """How much a PR changed the full-scan result (shows the scenario actually exercises something)."""
    findings = set(before["findings"]) ^ set(after["findings"])
    failed = sum(1 for k in findings if (before["findings"].get(k) or after["findings"].get(k))["status"] == "failed")
    vertices = set(before["graph"]["vertices"]) ^ set(after["graph"]["vertices"])
    changed = sum(1 for k in set(before["graph"]["vertices"]) & set(after["graph"]["vertices"])
                  if before["graph"]["vertices"][k] != after["graph"]["vertices"][k])
    return {"findings": len(findings), "FAILED": failed, "vertices_added_or_removed": len(vertices),
            "vertices_changed": changed}
