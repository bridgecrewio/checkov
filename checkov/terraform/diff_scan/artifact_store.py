"""On-disk layout of the baseline artifact (v3): one directory, one file per section, each section decoded only when
the diff scan first needs it and dropped as soon as it has been used.

  <dir>/manifest.json            format, artifact version, section list with sizes (small, read first)
  <dir>/<section>.msgpack.zst    one msgpack document per top-level artifact key, zstd-compressed

The JSON (v2) artifact is parsed in one piece and every decoded value stays referenced by the scan to the end. Here
the scan holds `ArtifactSections`, a dict-like view that decodes a section on first access (`a["edges"]`), and
`release(name)` drops the decoded value once nothing needs it any more. Sections are independent, so the peak holds
only what one phase reads.

Writing streams one section at a time (the baseline never builds a second serialized copy of the whole artifact).
msgpack was chosen over JSON / orjson / pickle by measured decode CPU and decoded size (results/round6), zstd level 3
by measured decompress cost (a few ms per section).
"""
from __future__ import annotations

import base64
import json
import os
import shutil
from typing import Any, Callable, Iterable, Iterator, Optional

import msgpack
import zstandard

FORMAT = "dfo-artifact-sections"
MANIFEST = "manifest.json"
SUFFIX = ".msgpack.zst"
ZSTD_LEVEL = 3


RECORD_ENCODING = "msgpack"
"""Rendered vertex records inside `rendered.vertices` are each kept as msgpack bytes: the diff scan decodes only the
records of frozen vertices it restores, one at a time."""


def encode_record(value: Any) -> bytes:
    return msgpack.packb(value, use_bin_type=True)


def decode_record(data: bytes) -> Any:
    return msgpack.unpackb(data, raw=False, strict_map_key=False)


def is_section_store(path: str) -> bool:
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, MANIFEST))


PICKLE_LIST_SECTIONS = ("vertices",)
"""Sections that are lists of base64 pickles in the v2 JSON artifact. The section store keeps them as raw pickle
bytes (base64 decoded at write time: -25 % bytes and no text copy at read time), written as a stream of items so a
read never holds the whole encoded section in one buffer next to its decoded form."""
ITEM_STREAM_MARKER = b"\xc1"
"""msgpack's never-used type byte: first byte of a section written as a stream of items (see _write_section)."""


def _write_section(path: str, name: str, value: Any) -> int:
    """msgpack -> zstd, streamed to the file: neither the full msgpack encoding nor the full compressed output is
    held in memory (the encoder works in chunks of top-level container items)."""
    compressor = zstandard.ZstdCompressor(level=ZSTD_LEVEL)
    with open(path, "wb") as f, compressor.stream_writer(f, closefd=False) as stream:
        packer = msgpack.Packer(use_bin_type=True)
        if name in PICKLE_LIST_SECTIONS:
            stream.write(ITEM_STREAM_MARKER)
            for item in value:
                stream.write(packer.pack(base64.b64decode(item)))
        elif isinstance(value, dict):
            stream.write(packer.pack_map_header(len(value)))
            for key, item in value.items():
                stream.write(packer.pack(key))
                stream.write(packer.pack(item))
        elif isinstance(value, list):
            stream.write(packer.pack_array_header(len(value)))
            for item in value:
                stream.write(packer.pack(item))
        else:
            stream.write(packer.pack(value))
    return os.path.getsize(path)


def _read_section(path: str) -> Any:
    """zstd -> msgpack, streamed from the file. A section written as a stream of items decodes item by item into a
    list (its encoded form is never buffered whole); any other section is one msgpack document."""
    with open(path, "rb") as f, zstandard.ZstdDecompressor().stream_reader(f) as stream:
        if stream.read(1) == ITEM_STREAM_MARKER:
            unpacker = msgpack.Unpacker(stream, raw=False, read_size=1 << 20, max_buffer_size=0)
            return [PickledItem(item) for item in unpacker]
    with open(path, "rb") as f, zstandard.ZstdDecompressor().stream_reader(f) as stream:
        unpacker = msgpack.Unpacker(stream, raw=False, strict_map_key=False, read_size=1 << 20, max_buffer_size=0)
        return unpacker.unpack()


class PickledItem(bytes):
    """Raw pickle bytes of an item of a PICKLE_LIST_SECTIONS section (artifact.loads accepts it as is)."""


class SectionWriter:
    """Writes sections one at a time as they are produced, into `<path>.partial`; `commit()` writes the manifest and
    moves the directory into place (a crash never leaves a half-written store at `path`)."""

    def __init__(self, path: str, version: int) -> None:
        self.path = path
        self.version = version
        self.scratch = path + ".partial"
        self.sizes: dict[str, int] = {}
        shutil.rmtree(self.scratch, ignore_errors=True)
        os.makedirs(self.scratch)

    def write(self, name: str, value: Any) -> None:
        if name in self.sizes:
            raise ValueError(f"section written twice: {name}")
        self.sizes[name] = _write_section(os.path.join(self.scratch, name + SUFFIX), name, value)

    def commit(self) -> dict[str, int]:
        with open(os.path.join(self.scratch, MANIFEST), "w") as f:
            json.dump({"format": FORMAT, "version": self.version, "sections": self.sizes}, f, indent=1)
        shutil.rmtree(self.path, ignore_errors=True)
        os.replace(self.scratch, self.path)
        return self.sizes


def write_sections(path: str, sections: Iterable[tuple[str, Any]], version: int) -> dict[str, int]:
    """Write each (name, value) as its own file, in order; returns name -> bytes on disk."""
    writer = SectionWriter(path, version)
    for name, value in sections:
        writer.write(name, value)
        del value
    return writer.commit()


class ArtifactSections:
    """Read-only, dict-like view of a section store. `a[name]` decodes the section on first access and keeps it until
    `release(name)`; reading a released section decodes it again (never stale, only slower)."""

    def __init__(self, path: str) -> None:
        with open(os.path.join(path, MANIFEST)) as f:
            manifest = json.load(f)
        if manifest.get("format") != FORMAT:
            raise ValueError(f"not a diff-scan artifact directory: {path}")
        self.path = path
        self.names: list[str] = list(manifest["sections"])
        self.sizes: dict[str, int] = dict(manifest["sections"])
        self.version = manifest["version"]
        self._loaded: dict[str, Any] = {}
        self.loads: dict[str, int] = {}
        self._relocate: Optional[Callable[[str, Any], Any]] = None
        self._overrides: dict[str, Any] = {}

    def relocate_on_load(self, relocate: Callable[[str, Any], Any], new_root: str) -> None:
        """Every section decoded from now on is passed through `relocate(name, value)` (relocate.relocate_section)."""
        self._relocate = relocate
        self._overrides = {"root": new_root}
        self._loaded.clear()

    def __getitem__(self, name: str) -> Any:
        if name in self._overrides:
            return self._overrides[name]
        if os.getenv("DFO_NEGATIVE", "") == "missing_section_file" and name == "rendered.vertices":
            raise KeyError(name)
        if name in self._loaded:
            return self._loaded[name]
        if name not in self.sizes:
            raise KeyError(name)
        value = _read_section(os.path.join(self.path, name + SUFFIX))
        if self._relocate is not None:
            value = self._relocate(name, value)
        self._loaded[name] = value
        self.loads[name] = self.loads.get(name, 0) + 1
        return value

    def get(self, name: str, default: Any = None) -> Any:
        return self[name] if name in self.sizes else default

    def __contains__(self, name: object) -> bool:
        return name in self.sizes

    def __iter__(self) -> Iterator[str]:
        return iter(self.names)

    def keys(self) -> list[str]:
        return list(self.names)

    def items(self) -> Iterator[tuple[str, Any]]:
        return ((name, self[name]) for name in self.names)

    def release(self, *names: str) -> None:
        for name in names:
            self._loaded.pop(name, None)

    def loaded(self) -> list[str]:
        return sorted(self._loaded)
