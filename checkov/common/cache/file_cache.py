from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from checkov.common.cache.utils import hash_file, hash_file_content
from checkov.common.util.json_utils import CustomJSONEncoder, object_hook
from checkov.common.util.type_forcers import convert_str_to_bool

USE_CACHE = convert_str_to_bool(os.getenv("CHECKOV_USE_CACHE", "True"))


class FileCache:
    def __init__(self) -> None:
        self.file_cache_path = Path(f"{tempfile.gettempdir()}/checkov_cache.json")
        self.cache: dict[str, Any] = {}

        # used for temporarily storing file_path to hash relation for non cached file content
        self._file_path_hash_map: dict[str, str] = {}

        self.load_cache()

    def load_cache(self) -> None:
        if USE_CACHE and self.file_cache_path.exists():
            self.cache = json.loads(self.file_cache_path.read_bytes(), object_hook=object_hook)

    def save_cache(self) -> None:
        if USE_CACHE:
            self.file_cache_path.write_text(json.dumps(self.cache, cls=CustomJSONEncoder))

    def load_definition(self, file_path: str, file_content: str | None = None) -> Any | None:
        if USE_CACHE:
            if file_content:
                file_hash = hash_file_content(file_content.encode("utf-8"))
            else:
                file_hash = hash_file(file_path)

            definition: dict[str, Any] | None = self.cache.get(f"{file_path}#{file_hash}")
            if not definition:
                self._file_path_hash_map[file_path] = file_hash

            return definition

        return None

    def save_definition(self, file_path: str, definition: Any) -> None:
        if USE_CACHE:
            file_hash = self._file_path_hash_map.get(file_path)
            if file_hash:
                self.cache[f"{file_path}#{file_hash}"] = definition


file_cache = FileCache()
