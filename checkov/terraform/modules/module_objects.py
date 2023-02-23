from __future__ import annotations

from typing import Optional, Any


class TFModule:
    __slots__ = ("path", "name", "foreach_idx")

    def __init__(self, path: str, name: str, foreach_idx: Optional[int | str] = None) -> None:
        self.path = path
        self.name = name
        self.foreach_idx = foreach_idx

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TFModule):
            return False
        return self.path == other.path and self.name == other.name and self.foreach_idx == other.foreach_idx

    def __repr__(self) -> str:
        return f'path:{self.path}, name:{self.name}, foreach_idx:{self.foreach_idx}'


class TFSourceModules:
    __slots__ = ("tf_source_modules", )

    def __init__(self, tf_source_modules: list[TFModule]) -> None:
        self.tf_source_modules = tf_source_modules

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TFSourceModules):
            return False
        return self.tf_source_modules == other.tf_source_modules

    def __repr__(self) -> str:
        return f'tf_source_modules:{self.tf_source_modules}'


class TFDefinitionKey:
    __slots__ = ("tf_source_modules", "file_path")

    def __init__(self, tf_source_modules: TFSourceModules, file_path: str) -> None:
        self.tf_source_modules = tf_source_modules
        self.file_path = file_path

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TFDefinitionKey):
            return False
        return self.tf_source_modules == other.tf_source_modules and self.file_path == other.file_path

    def __repr__(self) -> str:
        return f'tf_source_modules:{self.tf_source_modules}, file_path:{self.file_path}'
