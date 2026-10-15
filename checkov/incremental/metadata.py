"""Persisted metadata graph for incremental scanning.

Shape (JSON):
{
  "schema_version": 1,
  "fingerprint": {...},                    # checkov version, frameworks, checks/skip config, external checks hash
  "frameworks": {
    "<framework>": {
      "units": {
        "<unit id>": {
          "files": {"<repo-relative path>": "<sha256>"},    # every file the unit's result depends on
          "external_modules": {"<source:version>": "ref:..."|"mutable:..."|"missing"},
          "records": [ {serialized Record}, ... ]
        }
      },
      "file_owners": {"<repo-relative path>": ["<unit id>", ...]}   # reverse index of `files`
    }
  }
}

Paths are repository-relative so the metadata can be produced on one checkout and consumed on another.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

METADATA_SCHEMA_VERSION = 1


def file_sha256(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return "MISSING"


def tree_sha256(directory: str) -> str:
    digest = hashlib.sha256()
    for root, dirs, files in sorted(os.walk(directory)):
        dirs.sort()
        for name in sorted(files):
            path = os.path.join(root, name)
            digest.update(os.path.relpath(path, directory).encode())
            digest.update(file_sha256(path).encode())
    return digest.hexdigest()


@dataclass
class UnitMetadata:
    files: dict[str, str]
    records: list[dict[str, Any]] = field(default_factory=list)
    external_modules: dict[str, str] = field(default_factory=dict)


@dataclass
class FrameworkMetadata:
    units: dict[str, UnitMetadata] = field(default_factory=dict)

    def file_owners(self) -> dict[str, list[str]]:
        owners: dict[str, list[str]] = {}
        for unit_id, unit in self.units.items():
            for path in unit.files:
                owners.setdefault(path, []).append(unit_id)
        return {path: sorted(units) for path, units in sorted(owners.items())}


@dataclass
class MetadataGraph:
    fingerprint: dict[str, Any]
    frameworks: dict[str, FrameworkMetadata] = field(default_factory=dict)
    schema_version: int = METADATA_SCHEMA_VERSION

    def to_json(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "fingerprint": self.fingerprint,
            "frameworks": {
                name: {"units": {uid: asdict(u) for uid, u in fw.units.items()}, "file_owners": fw.file_owners()}
                for name, fw in self.frameworks.items()
            },
        }

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_json(), f, indent=1, sort_keys=True, default=str)

    @staticmethod
    def load(path: str) -> Optional["MetadataGraph"]:
        if not os.path.exists(path):
            return None
        with open(path) as f:
            raw = json.load(f)
        if raw.get("schema_version") != METADATA_SCHEMA_VERSION:
            return None
        frameworks = {
            name: FrameworkMetadata(units={uid: UnitMetadata(**u) for uid, u in fw["units"].items()})
            for name, fw in raw["frameworks"].items()
        }
        return MetadataGraph(fingerprint=raw["fingerprint"], frameworks=frameworks)
