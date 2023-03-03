from __future__ import annotations

from typing import Optional, Any


class TFModule:
    __slots__ = ("path", "index", "foreach_idx", "nested_tf_module")

    def __init__(self, path: str, index: int, nested_tf_module: Optional[TFModule] = None, foreach_idx: Optional[int | str] = None) -> None:
        self.path = path
        self.index = index
        self.foreach_idx = foreach_idx
        self.nested_tf_module = nested_tf_module

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TFModule):
            return False
        return self.path == other.path and self.index == other.index and self.nested_tf_module == other.nested_tf_module and self.foreach_idx == other.foreach_idx

    def __repr__(self) -> str:
        return f'path:{self.path}, name:{self.index}, nested_tf_module:{self.nested_tf_module}, foreach_idx:{self.foreach_idx}'

    def __hash__(self) -> int:
        return hash((self.path, self.index, self.nested_tf_module, self.foreach_idx))


class TFDefinitionKey:
    __slots__ = ("tf_source_modules", "file_path")

    def __init__(self, file_path: str, tf_source_modules: Optional[TFModule] = None) -> None:
        self.tf_source_modules = tf_source_modules
        self.file_path = file_path

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TFDefinitionKey):
            return False
        return self.tf_source_modules == other.tf_source_modules and self.file_path == other.file_path

    def __repr__(self) -> str:
        return f'tf_source_modules:{self.tf_source_modules}, file_path:{self.file_path}'

    def __hash__(self) -> int:
        return hash((self.file_path, self.tf_source_modules))
