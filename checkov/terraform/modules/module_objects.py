from __future__ import annotations
import json
from collections.abc import Iterator
from typing import Optional, Any


class TFModule:
    __slots__ = ("path", "name", "foreach_idx", "nested_tf_module")

    def __init__(self, path: str, name: str | None, nested_tf_module: Optional[TFModule] = None,
                 foreach_idx: Optional[int | str] = None) -> None:
        self.path = path
        self.name = name
        self.foreach_idx = foreach_idx
        self.nested_tf_module = nested_tf_module

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TFModule):
            return False
        return self.path == other.path and self.name == other.name and self.nested_tf_module == other.nested_tf_module and self.foreach_idx == other.foreach_idx

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, TFModule):
            return False
        return (self.path, self.name, self.nested_tf_module, self.foreach_idx) < (
            other.path, other.name, other.nested_tf_module, other.foreach_idx)

    def __repr__(self) -> str:
        return f'path:{self.path}, name:{self.name}, nested_tf_module:{self.nested_tf_module}, foreach_idx:{self.foreach_idx}'

    def __hash__(self) -> int:
        return hash((self.path, self.name, self.nested_tf_module, self.foreach_idx))

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        yield from {
            "path": self.path,
            "name": self.name,
            "foreach_idx": self.foreach_idx,
            "nested_tf_module": dict(self.nested_tf_module) if self.nested_tf_module else None
        }.items()

    def __str__(self) -> str:
        from checkov.common.util.json_utils import CustomJSONEncoder
        return json.dumps(dict(self), cls=CustomJSONEncoder)

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> TFModule | None:
        return TFModule(path=json_dct['path'], name=json_dct['name'], foreach_idx=json_dct['foreach_idx'],
                        nested_tf_module=TFModule.from_json(json_dct['nested_tf_module']) if json_dct.get(
                            'nested_tf_module') else None) if json_dct else None


class TFDefinitionKey:
    __slots__ = ("tf_source_modules", "file_path")

    def __init__(self, file_path: str, tf_source_modules: Optional[TFModule] = None) -> None:
        self.tf_source_modules = tf_source_modules
        self.file_path = file_path

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TFDefinitionKey):
            return False
        return self.tf_source_modules == other.tf_source_modules and self.file_path == other.file_path

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, TFDefinitionKey):
            return False
        return (self.file_path, self.tf_source_modules) < (other.file_path, other.tf_source_modules)

    def __repr__(self) -> str:
        return f'tf_source_modules:{self.tf_source_modules}, file_path:{self.file_path}'

    def __hash__(self) -> int:
        return hash((self.file_path, self.tf_source_modules))

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        yield from {
            "file_path": self.file_path,
            "tf_source_modules": dict(self.tf_source_modules) if self.tf_source_modules else None
        }.items()

    def __str__(self) -> str:
        from checkov.common.util.json_utils import CustomJSONEncoder
        return json.dumps(self.to_json(), cls=CustomJSONEncoder)

    def to_json(self) -> dict[str, Any]:
        to_return: dict[str, Any] = {"file_path": self.file_path, "tf_source_modules": None}
        if self.tf_source_modules:
            to_return["tf_source_modules"] = dict(self.tf_source_modules)
        return to_return

    @staticmethod
    def from_json(json_dct: dict[str, Any]) -> TFDefinitionKey:
        return TFDefinitionKey(file_path=json_dct['file_path'],
                               tf_source_modules=TFModule.from_json(json_dct['tf_source_modules']))
