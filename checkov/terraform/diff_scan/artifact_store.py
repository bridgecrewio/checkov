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


INDEXED_RECORD_SECTIONS = ("rendered.vertices", "findings.vertices")
"""Sections that are {key: encoded record} maps read record by record: written as an indexed record file instead of
one msgpack map, so a read keeps only the index (key -> offset, length) and pulls a record's bytes on demand. gcp:
the rendered vertex records are 280 MB once decompressed; loading them as one map cost +350 MB at the render step."""
RECORDS_SUFFIX = ".records"


def indexed_records_enabled() -> bool:
    return os.getenv("CHECKOV_DIFF_INDEXED_RECORDS", "false").lower() == "true"


def _write_indexed_records(path: str, value: dict[str, bytes]) -> int:
    """`<path>`: zstd-compressed msgpack index {key: [offset, length]}; `<path>.records`: the raw record bytes
    concatenated (each record is already a msgpack document; not compressed, so a record is read with one seek)."""
    index: dict[str, list[int]] = {}
    offset = 0
    with open(path + RECORDS_SUFFIX, "wb") as records:
        for key, record in value.items():
            records.write(record)
            index[key] = [offset, len(record)]
            offset += len(record)
    compressor = zstandard.ZstdCompressor(level=ZSTD_LEVEL)
    with open(path, "wb") as f, compressor.stream_writer(f, closefd=False) as stream:
        stream.write(INDEXED_RECORDS_MARKER)
        stream.write(msgpack.packb(index, use_bin_type=True))
    return os.path.getsize(path) + os.path.getsize(path + RECORDS_SUFFIX)


INDEXED_RECORDS_MARKER = b"\xc7"
"""First byte of an indexed record section (msgpack ext8 header byte: never the first byte of a map or array)."""


class IndexedRecords:
    """Read-only mapping key -> record bytes of an indexed record section: the index is in memory, each record is
    read from disk on access (and not kept)."""

    def __init__(self, records_path: str, index: dict[str, list[int]]) -> None:
        self._path = records_path
        self._index = index
        self._file = open(records_path, "rb")  # noqa: SIM115  # closed by close() / garbage collection

    def __getitem__(self, key: str) -> bytes:
        offset, length = self._index[key]
        if os.getenv("DFO_NEGATIVE", "") == "indexed_records_off_by_one":
            offset += 1
        self._file.seek(offset)
        data = self._file.read(length)
        if len(data) != length:
            raise ValueError(f"truncated record in {self._path}: {key}")
        return data

    def __contains__(self, key: object) -> bool:
        return key in self._index

    def __iter__(self) -> Iterator[str]:
        return iter(self._index)

    def __len__(self) -> int:
        return len(self._index)

    def keys(self) -> Any:
        return self._index.keys()

    def items(self) -> Iterator[tuple[str, bytes]]:
        return ((key, self[key]) for key in self._index)

    def values(self) -> Iterator[bytes]:
        return (self[key] for key in self._index)

    def get(self, key: str, default: Any = None) -> Any:
        return self[key] if key in self._index else default

    def close(self) -> None:
        self._file.close()

    def __del__(self) -> None:
        try:
            self._file.close()
        except Exception:  # noqa: S110  # best effort at interpreter shutdown
            pass


INDEXED_LIST_MARKER = b"\xc8"
"""First byte of an indexed list section (msgpack ext16 header byte: never the first byte of a map or array)."""


class IndexedList:
    """Read-only sequence of PickledItem records read from `<path>.records` on demand (one seek per item)."""

    def __init__(self, records_path: str, offsets: list[list[int]],
                 transform: Optional[Callable[[bytes], Any]] = None) -> None:
        self._path = records_path
        self._offsets = offsets
        self._transform = transform
        self._file = open(records_path, "rb")  # noqa: SIM115  # closed by close() / garbage collection

    def __getitem__(self, index: int) -> Any:
        offset, length = self._offsets[index]
        if os.getenv("DFO_NEGATIVE", "") == "indexed_list_off_by_one":
            offset += 1
        self._file.seek(offset)
        data = self._file.read(length)
        if len(data) != length:
            raise ValueError(f"truncated item in {self._path}: {index}")
        item: Any = PickledItem(data)
        return self._transform(item) if self._transform is not None else item

    def with_transform(self, fn: Callable[[bytes], Any]) -> "IndexedList":
        prev = self._transform
        return IndexedList(self._path, self._offsets, (lambda b: fn(prev(b))) if prev is not None else fn)

    def __len__(self) -> int:
        return len(self._offsets)

    def __iter__(self) -> Iterator[Any]:
        return (self[i] for i in range(len(self._offsets)))

    def close(self) -> None:
        self._file.close()

    def __del__(self) -> None:
        try:
            self._file.close()
        except Exception:  # noqa: S110
            pass


def _write_indexed_list(path: str, items: Iterable[bytes]) -> int:
    """`<path>`: zstd-compressed msgpack list of [offset, length]; `<path>.records`: raw bytes concatenated."""
    offsets: list[list[int]] = []
    offset = 0
    with open(path + RECORDS_SUFFIX, "wb") as records:
        for raw in items:
            records.write(raw)
            offsets.append([offset, len(raw)])
            offset += len(raw)
    compressor = zstandard.ZstdCompressor(level=ZSTD_LEVEL)
    with open(path, "wb") as f, compressor.stream_writer(f, closefd=False) as stream:
        stream.write(INDEXED_LIST_MARKER)
        stream.write(msgpack.packb(offsets, use_bin_type=True))
    return os.path.getsize(path) + os.path.getsize(path + RECORDS_SUFFIX)


DEFINITION_INDEX_MARKER = b"\xc9"
"""First byte of an indexed definitions section: metadata in `<path>`, raw definition pickles in `<path>.records`."""


class IndexedDefinitions:
    """List-like view of `definitions` entries where each entry's `definition` pickle is read from `<path>.records`
    on demand (`entry["definition"]` seeks and reads; `entry["key"]`, `resource_types`, `vertices` are in memory)."""

    def __init__(self, records_path: str, entries: list[dict[str, Any]],
                 transform_definition: Optional[Callable[[bytes], Any]] = None) -> None:
        self._path = records_path
        self._file = open(records_path, "rb")  # noqa: SIM115
        self._transform = transform_definition
        self._entries = [IndexedDefinitionEntry(self, e) for e in entries]

    def read_definition(self, offset: int, length: int) -> Any:
        if os.getenv("DFO_NEGATIVE", "") == "stale_indexed_definition":
            offset += 1
        self._file.seek(offset)
        data = self._file.read(length)
        if len(data) != length:
            raise ValueError(f"truncated definition in {self._path}@{offset}")
        item: Any = PickledItem(data)
        return self._transform(item) if self._transform is not None else item

    def with_transform(self, fn: Callable[[dict[str, Any]], dict[str, Any]],
                       def_fn: Callable[[bytes], Any]) -> "IndexedDefinitions":
        prev = self._transform
        chained = (lambda b: def_fn(prev(b))) if prev is not None else def_fn
        raw_entries = [fn(e._raw_meta()) for e in self._entries]
        return IndexedDefinitions(self._path, raw_entries, chained)

    def __getitem__(self, index: int) -> "IndexedDefinitionEntry":
        return self._entries[index]

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator["IndexedDefinitionEntry"]:
        return iter(self._entries)

    def close(self) -> None:
        self._file.close()

    def __del__(self) -> None:
        try:
            self._file.close()
        except Exception:  # noqa: S110
            pass


class IndexedDefinitionEntry(dict):  # type: ignore[type-arg]
    """Dict-like definition entry (`key`, `resource_types`, `vertices`, and lazy `definition`)."""

    def __init__(self, owner: IndexedDefinitions, meta: dict[str, Any]) -> None:
        super().__init__(
            {k: v for k, v in meta.items() if k not in ("key", "offset", "length")},
        )
        if "key" in meta:
            self["key"] = PickledItem(meta["key"]) if isinstance(meta["key"], bytes) else meta["key"]
        self._owner = owner
        self._offset: int = meta["offset"]
        self._length: int = meta["length"]

    def _raw_meta(self) -> dict[str, Any]:
        d = {k: v for k, v in self.items() if k != "definition"}
        d["offset"] = self._offset
        d["length"] = self._length
        return d

    def with_vertices(self, vertices: list[int]) -> "IndexedDefinitionEntry":
        return IndexedDefinitionEntry(self._owner, {**self._raw_meta(), "vertices": vertices})

    def __getitem__(self, k: str) -> Any:
        if k == "definition" and "definition" not in self:
            return self._owner.read_definition(self._offset, self._length)
        return super().__getitem__(k)

    def get(self, k: str, default: Any = None) -> Any:
        if k == "definition":
            return self["definition"]
        return super().get(k, default)


def _write_indexed_definitions(path: str, entries: list[dict[str, Any]]) -> int:
    meta: list[dict[str, Any]] = []
    offset = 0
    with open(path + RECORDS_SUFFIX, "wb") as records:
        for d in entries:
            raw_def = d["definition"] if isinstance(d["definition"], bytes) else base64.b64decode(d["definition"])
            raw_key = d["key"] if isinstance(d["key"], bytes) else base64.b64decode(d["key"])
            records.write(raw_def)
            entry_meta = {k: v for k, v in d.items() if k != "definition"}
            entry_meta.update(key=raw_key, offset=offset, length=len(raw_def))
            meta.append(entry_meta)
            offset += len(raw_def)
    compressor = zstandard.ZstdCompressor(level=ZSTD_LEVEL)
    with open(path, "wb") as f, compressor.stream_writer(f, closefd=False) as stream:
        stream.write(DEFINITION_INDEX_MARKER)
        stream.write(msgpack.packb(meta, use_bin_type=True))
    return os.path.getsize(path) + os.path.getsize(path + RECORDS_SUFFIX)


def _write_section(path: str, name: str, value: Any) -> int:
    """msgpack -> zstd, streamed to the file: neither the full msgpack encoding nor the full compressed output is
    held in memory (the encoder works in chunks of top-level container items)."""
    if name in INDEXED_RECORD_SECTIONS and isinstance(value, dict) and indexed_records_enabled():
        return _write_indexed_records(path, value)
    if name in PICKLE_LIST_SECTIONS and indexed_records_enabled():
        return _write_indexed_list(path, (i if isinstance(i, bytes) else base64.b64decode(i) for i in value))
    if name == "definitions" and isinstance(value, list) and indexed_records_enabled():
        return _write_indexed_definitions(path, value)
    compressor = zstandard.ZstdCompressor(level=ZSTD_LEVEL)
    with open(path, "wb") as f, compressor.stream_writer(f, closefd=False) as stream:
        packer = msgpack.Packer(use_bin_type=True)
        if name in PICKLE_LIST_SECTIONS:
            stream.write(ITEM_STREAM_MARKER)
            for item in value:
                stream.write(packer.pack(base64.b64decode(item)))
        elif name in ("rendered.edges", "edges", "keys", "creation_digests", "fingerprints", "unit_by_vertex") \
                and isinstance(value, list):
            stream.write(ITEM_STREAM_MARKER)
            for item in value:
                stream.write(packer.pack(item))
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
        first = stream.read(1)
        if first == ITEM_STREAM_MARKER:
            unpacker = msgpack.Unpacker(stream, raw=False, read_size=1 << 20, max_buffer_size=0)
            return [PickledItem(item) if isinstance(item, bytes) else item for item in unpacker]
        if first == INDEXED_RECORDS_MARKER:
            index = msgpack.unpackb(stream.read(), raw=False, strict_map_key=False)
            return IndexedRecords(path + RECORDS_SUFFIX, index)
        if first == INDEXED_LIST_MARKER:
            offsets = msgpack.unpackb(stream.read(), raw=False, strict_map_key=False)
            return IndexedList(path + RECORDS_SUFFIX, offsets)
        if first == DEFINITION_INDEX_MARKER:
            meta = msgpack.unpackb(stream.read(), raw=False, strict_map_key=False)
            return IndexedDefinitions(path + RECORDS_SUFFIX, meta)
    with open(path, "rb") as f, zstandard.ZstdDecompressor().stream_reader(f) as stream:
        unpacker = msgpack.Unpacker(stream, raw=False, strict_map_key=False, read_size=1 << 20, max_buffer_size=0)
        return unpacker.unpack()


class PickledItem(bytes):
    """Raw pickle bytes of an item of a PICKLE_LIST_SECTIONS section (artifact.loads accepts it as is)."""


PICKLE_CARRYING_SECTIONS = frozenset({"vertices", "tfvar_blocks", "module", "definitions", "alias_keys",
                                      "variable_inputs"})
"""Sections holding pickles, base64 text in v2 (relocate.PICKLED_* and the alias / variable-input fields): a root
inside a pickle is invisible to a string search, so these are never declared root-free."""


def is_plain_root_free(value: Any, root: str, name: str = "") -> bool:
    """True if `value` is built only of dict / list / tuple / str / bytes-free scalars, no str in it (dict keys
    included) contains `root`, and section `name` carries no pickles. Anything else is never declared root-free."""
    if name in PICKLE_CARRYING_SECTIONS:
        return False
    stack = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, str):
            if root in item:
                return False
        elif isinstance(item, dict):
            stack.extend(item.keys())
            stack.extend(item.values())
        elif isinstance(item, (list, tuple)):
            stack.extend(item)
        elif not (item is None or isinstance(item, (int, float, bool))):
            return False
    return True


class SectionWriter:
    """Writes sections one at a time as they are produced, into `<path>.partial`; `commit()` writes the manifest and
    moves the directory into place (a crash never leaves a half-written store at `path`)."""

    def __init__(self, path: str, version: int, root: Optional[str] = None) -> None:
        self.path = path
        self.version = version
        self.root = root
        """the baseline root: when given, the manifest lists the plain sections that contain no string holding it"""
        self.scratch = path + ".partial"
        self.sizes: dict[str, int] = {}
        self.root_free: list[str] = []
        shutil.rmtree(self.scratch, ignore_errors=True)
        os.makedirs(self.scratch)

    def write(self, name: str, value: Any) -> None:
        if name in self.sizes:
            raise ValueError(f"section written twice: {name}")
        if self.root is not None and name != "root" and is_plain_root_free(value, self.root, name):
            self.root_free.append(name)
        self.sizes[name] = _write_section(os.path.join(self.scratch, name + SUFFIX), name, value)

    def commit(self) -> dict[str, int]:
        manifest: dict[str, Any] = {"format": FORMAT, "version": self.version, "sections": self.sizes}
        if self.root is not None:
            manifest["root_free_sections"] = sorted(self.root_free)
        with open(os.path.join(self.scratch, MANIFEST), "w") as f:
            json.dump(manifest, f, indent=1)
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
        self.root_free_sections: frozenset[str] = frozenset(manifest.get("root_free_sections", ()))
        """written by the baseline (SectionWriter): relocation returns these sections untouched"""
        self._loaded: dict[str, Any] = {}
        self.loads: dict[str, int] = {}
        self._relocate: Optional[Callable[[str, Any], Any]] = None
        self._overrides: dict[str, Any] = {}

    def relocate_on_load(self, relocate: Callable[[str, Any], Any], new_root: str) -> None:
        """Every section decoded from now on is passed through `relocate(name, value)` (relocate.relocate_section)."""
        self._relocate = relocate
        self._overrides = {"root": new_root}
        self._loaded.clear()

    def remap_on_load(self, remap: Callable[[str, Any], Any]) -> None:
        """Every section decoded from now on is also passed through `remap(name, value)` (rename.section_remapper),
        after any relocation. Sections already decoded are remapped now."""
        previous = self._relocate

        def chained(name: str, value: Any) -> Any:
            return remap(name, previous(name, value) if previous is not None else value)

        self._relocate = chained
        self._loaded = {name: remap(name, value) for name, value in self._loaded.items()}

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
