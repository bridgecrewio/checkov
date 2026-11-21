from __future__ import annotations
import json
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, eq=False)
class TFModule:
    path: str
    name: str | None
    nested_tf_module: TFModule | None = None
    foreach_idx: int | str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "_hash", hash((self.path, self.name, self.nested_tf_module, self.foreach_idx)))

    def __hash__(self) -> int:
        h = getattr(self, "_hash", None)
        if h is None:
            h = hash((self.path, self.name, self.nested_tf_module, self.foreach_idx))
            object.__setattr__(self, "_hash", h)
        return h

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, TFModule) or hash(self) != hash(other):
            return False
        return (self.path == other.path and self.name == other.name
                and self.foreach_idx == other.foreach_idx and self.nested_tf_module == other.nested_tf_module)

    def __setstate__(self, state: dict[str, Any]) -> None:
        for k, v in state.items():
            object.__setattr__(self, k, v)
        object.__setattr__(self, "_hash", hash((self.path, self.name, self.nested_tf_module, self.foreach_idx)))

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, TFModule):
            return False
        return (self.path, self.name, self.nested_tf_module, self.foreach_idx) < (
            other.path, other.name, other.nested_tf_module, other.foreach_idx)

    def __repr__(self) -> str:
        return f'path:{self.path}, name:{self.name}, nested_tf_module:{self.nested_tf_module}, foreach_idx:{self.foreach_idx}'

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
    def from_json(json_dct: dict[str, Any] | None) -> TFModule | None:
        if not json_dct:
            return None
        foreach_idx = json_dct['foreach_idx']
        if isinstance(foreach_idx, str) and foreach_idx.isnumeric():
            foreach_idx = int(foreach_idx)
        return TFModule(path=json_dct['path'], name=json_dct['name'], foreach_idx=foreach_idx,
                        nested_tf_module=TFModule.from_json(json_dct.get('nested_tf_module')) if json_dct.get(
                            'nested_tf_module') else None)


@dataclass(frozen=True, eq=False)
class TFDefinitionKey:
    file_path: str
    tf_source_modules: TFModule | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "_hash", hash((self.file_path, self.tf_source_modules)))

    def __hash__(self) -> int:
        h = getattr(self, "_hash", None)
        if h is None:
            h = hash((self.file_path, self.tf_source_modules))
            object.__setattr__(self, "_hash", h)
        return h

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if not isinstance(other, TFDefinitionKey) or hash(self) != hash(other):
            return False
        return self.file_path == other.file_path and self.tf_source_modules == other.tf_source_modules

    def __setstate__(self, state: dict[str, Any]) -> None:
        for k, v in state.items():
            object.__setattr__(self, k, v)
        object.__setattr__(self, "_hash", hash((self.file_path, self.tf_source_modules)))

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, TFDefinitionKey):
            return False
        return (self.file_path, self.tf_source_modules) < (other.file_path, other.tf_source_modules)

    def __repr__(self) -> str:
        return f'tf_source_modules:{self.tf_source_modules}, file_path:{self.file_path}'

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
