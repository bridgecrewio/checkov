"""Rename-aware remap: a pure, order-preserving file rename is applied to the artifact instead of re-parsing.

A rename B:<dir>/old.tf -> T:<dir>/new.tf qualifies when (rename_pairs):
  * both paths are in the same directory and the new file's content is byte-identical to the baseline's stored
    content of the old file;
  * the rename keeps the file's rank among the directory's Terraform files in sorted order. Checkov loads a
    directory's files in sorted order, and that order is observable: a module call's `__resolved__` lists the loaded
    files, and when two blocks of one directory write the same attribute the later file wins (a rank-changing rename
    changes findings: doc/RENAME_POC_PLAN.md, probe 1);
  * neither path is a variable file (tfvars routing is by path) and no other file of that directory changes.

Then a full scan of T equals a full scan of B with every occurrence of the old path replaced by the new one
(verified on real repositories: graph and findings identical). So the artifact is remapped with the relocation
machinery, Relocator(<root>/<dir>/old.tf, <root>/<dir>/new.tf), on every section, including the anonymised rendered
export ("<root>/<dir>/old.tf"), and the rename is dropped from the change set. The engine then sees an unchanged
file and splices everything.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable, Optional

from checkov.terraform.diff_scan.artifact_store import decode_record, encode_record
from checkov.terraform.diff_scan.relocate import Relocator, relocate_section
from checkov.terraform.diff_scan.tfvars import is_terraform_file, is_variable_file
from checkov.terraform.graph_builder.incremental_graph import ROOT

RENAME_REMAP_ENV = "CHECKOV_DIFF_RENAME_REMAP"
"""Opt-in (set by the diff scan)."""

NEGATIVE_CONTROL = os.getenv("DFO_NEGATIVE", "")


def rename_remap_enabled() -> bool:
    return os.getenv(RENAME_REMAP_ENV, "false").lower() == "true"


def _directory_files(stored: dict[str, Any], directory: str) -> list[str]:
    """Baseline Terraform files of one directory (the artifact's stored file contents)."""
    return sorted(p for p in stored if os.path.dirname(p) == directory and is_terraform_file(p))


def _keeps_rank(old: str, new: str, directory_files: list[str]) -> bool:
    names = [os.path.basename(p) for p in directory_files]
    after = sorted([n for n in names if n != os.path.basename(old)] + [os.path.basename(new)])
    if NEGATIVE_CONTROL == "rename_ignore_order":
        return True
    return names.index(os.path.basename(old)) == after.index(os.path.basename(new))


def _read_lines(path: str) -> list[str]:
    with open(path) as f:
        return f.readlines()


def rename_pairs(stored: dict[str, Any], changed: list[str], deleted: list[str]) -> list[tuple[str, str]]:
    """(old, new) absolute paths of qualifying renames (module docstring)."""
    pairs: list[tuple[str, str]] = []
    touched_directories = [os.path.dirname(p) for p in changed + deleted]
    for old in deleted:
        if old not in stored or is_variable_file(old) or not is_terraform_file(old):
            continue
        directory = os.path.dirname(old)
        if touched_directories.count(directory) != 2:
            continue
        candidates = [p for p in changed if os.path.dirname(p) == directory and is_terraform_file(p)
                      and not is_variable_file(p) and p not in stored]
        if len(candidates) != 1:
            continue
        new = candidates[0]
        if _read_lines(new) != stored[old]:
            continue
        if not _keeps_rank(old, new, _directory_files(stored, directory)):
            continue
        pairs.append((old, new))
    return pairs


class _FileRenamer(Relocator):
    """Relocator whose "root" is one file path: exact match or the path followed by a quote / separator never
    occurs inside other paths, so a plain substring replacement of the absolute path is exact. Every absolute
    path in the artifact that names the old file is `<root>/<dir>/old.tf` (TFDefinitionKey.file_path, vertex
    path, __resolved__ entries, breadcrumbs, module chains)."""

    def __init__(self, old: str, new: str) -> None:
        super().__init__(old, new)

    def text(self, value: str) -> str:
        return value.replace(self.old, self.new) if self.old in value else value

    def pickled(self, text: str | bytes) -> str | bytes:
        """Raw pickles (v3 store) that do not contain the old path are returned untouched, without unpickling:
        pickle stores str as UTF-8, so absence of the bytes proves absence of the path."""
        if isinstance(text, bytes) and self.old.encode() not in text:
            return text
        return super().pickled(text)


def _anonymised_path(path: str, root: str) -> str:
    return ROOT + path[len(root):]


def _renamed_json_text(value: Any, old: str, new: str) -> Any:
    """JSON-safe values (anonymised rendered export, pre-render digests, edge strings): substring replacement on the
    JSON text. The anonymised path is followed by a closing quote or an escaped quote in every occurrence."""
    text = json.dumps(value)
    if old not in text:
        return value
    return json.loads(text.replace(old, new))


class RenamedRecords:
    """Read-only view of an indexed record section with one file path renamed: keys and each record's bytes are
    rewritten on access (records not mentioning the old path are returned as stored)."""

    def __init__(self, base: Any, old: str, new: str) -> None:
        self._base = base
        self._old, self._new = old, new
        self._needle = old.encode()
        self._to_base = {(k.replace(old, new) if old in k else k): k for k in base.keys()}

    def __getitem__(self, key: str) -> bytes:
        record = self._base[self._to_base[key]]
        if self._needle not in record:
            return record
        return encode_record(_renamed_json_text(decode_record(record), self._old, self._new))

    def __contains__(self, key: object) -> bool:
        return key in self._to_base

    def __iter__(self) -> Any:
        return iter(self._to_base)

    def __len__(self) -> int:
        return len(self._to_base)

    def keys(self) -> Any:
        return self._to_base.keys()

    def items(self) -> Any:
        return ((key, self[key]) for key in self._to_base)

    def values(self) -> Any:
        return (self[key] for key in self._to_base)

    def get(self, key: str, default: Any = None) -> Any:
        return self[key] if key in self._to_base else default


def _remap_rendered_vertices(value: dict[str, Any], old: str, new: str, encoded: bool) -> dict[str, Any]:
    """Encoded records (msgpack, UTF-8 strings) are decoded only when their bytes contain the old path. A read-only
    indexed record section (artifact_store.IndexedRecords) becomes a RenamedRecords overlay instead of a copy."""
    from checkov.terraform.diff_scan.artifact_store import IndexedRecords

    if isinstance(value, IndexedRecords):
        return RenamedRecords(value, old, new)  # type: ignore[return-value]
    needle = old.encode()
    for key in list(value):
        record = value[key]
        mentions = needle in record if encoded else old in json.dumps(record)
        if mentions:
            decoded = _renamed_json_text(decode_record(record) if encoded else record, old, new)
            record = encode_record(decoded) if encoded else decoded
        if old in key:
            del value[key]
            value[key.replace(old, new)] = record
        elif mentions:
            value[key] = record
    return value


def _remap_pre_render(value: dict[str, Any], anonymised: list[tuple[str, str]]) -> dict[str, Any]:
    """Keys, edges and the digest map's keys are renamed. The digest VALUES are hashes of anonymised pre-render
    states holding the OLD path; they stay, and the PR side hashes with new paths mapped back to old ones
    (incremental_graph.PATH_RENAMES), so an unchanged vertex still matches. The same holds for creation digests and
    count / for_each closure signatures."""
    for old, new in anonymised:
        value = _renamed_entries(value, old, new)
    return value


def _renamed_entries(value: Any, old: str, new: str) -> Any:
    """Per-entry substitution for large containers of strings (pre-render keys / edges / digest map, rendered edges):
    no whole-section JSON text, so no transient copy of the section (vpc: -67 MB / -48 MB peak)."""
    if isinstance(value, str):
        return value.replace(old, new) if old in value else value
    if isinstance(value, list):
        return [_renamed_entries(v, old, new) for v in value]
    if isinstance(value, dict):
        return {(k.replace(old, new) if isinstance(k, str) and old in k else k): _renamed_entries(v, old, new)
                for k, v in value.items()}
    return value


def section_remapper(pairs: list[tuple[str, str]], root: str, encoded_vertices: bool) \
        -> Callable[[str, Any], Any]:
    """remap(name, value) for every artifact section, applying every rename in order."""
    anonymised = [(_anonymised_path(o, root), _anonymised_path(n, root)) for o, n in pairs]

    def remap(name: str, value: Any) -> Any:
        if name == "baseline_inputs":
            return value
        if name == "rendered.pre_render":
            return _remap_pre_render(value, anonymised)
        if name == "rendered.vertices":
            for old, new in anonymised:
                value = _remap_rendered_vertices(value, old, new, encoded_vertices)
            return value
        if name == "expansions":
            for old, new in anonymised:
                value = {key.replace(old, new): record for key, record in value.items()}
            return value
        if name in ("rendered", "rendered.edges", "keys", "units", "unit_by_vertex"):
            for old, new in anonymised + list(pairs):
                value = _renamed_entries(value, old, new)
            return value
        if name == "files":
            for old, new in pairs:
                value = {(new if p == old else p): lines for p, lines in value.items()}
            return value
        for old, new in pairs:
            value = relocate_section(name, value, _FileRenamer(old, new))
        return value

    return remap


def apply_renames(artifact: Any, root: str, changed: list[str], deleted: list[str],
                  encoded_vertices: bool) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    """Remap `artifact` in place for every qualifying rename; returns the remaining (changed, deleted) and the
    applied pairs. The artifact must already be relocated to `root`."""
    if not rename_remap_enabled():
        return changed, deleted, []
    pairs = rename_pairs(artifact["files"], changed, deleted)
    if not pairs:
        return changed, deleted, []
    remap = section_remapper(pairs, root, encoded_vertices)
    install = getattr(artifact, "remap_on_load", None)
    if install is not None:
        install(remap)
    else:
        for name in list(artifact.keys()):
            if name == "rendered":
                rendered = artifact[name]
                artifact[name] = {**remap("rendered", {k: v for k, v in rendered.items() if k != "vertices"}),
                                  "vertices": remap("rendered.vertices", rendered["vertices"])}
            else:
                artifact[name] = remap(name, artifact[name])
    from checkov.terraform.graph_builder import incremental_graph

    incremental_graph.PATH_RENAMES[:] = [(_anonymised_path(o, root), _anonymised_path(n, root)) for o, n in pairs]
    if NEGATIVE_CONTROL == "rename_no_digest_backmap":
        incremental_graph.PATH_RENAMES[:] = []
    olds, news = {o for o, _ in pairs}, {n for _, n in pairs}
    return [p for p in changed if p not in news], [p for p in deleted if p not in olds], pairs


def pairs_report(pairs: list[tuple[str, str]], root: str) -> list[dict[str, str]]:
    return [{"from": os.path.relpath(o, root), "to": os.path.relpath(n, root)} for o, n in pairs]


def expected_renames(changed: list[str], deleted: list[str]) -> Optional[int]:
    """Same-directory (deleted, changed) pairs: a rename candidate before content / order checks (for the report)."""
    return sum(1 for o in deleted if any(os.path.dirname(o) == os.path.dirname(n) for n in changed))
