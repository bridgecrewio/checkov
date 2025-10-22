from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VarReference:
    definition_name: str               # Example: 'region'
    definition_expression: str         # Example: '${var.region}'
    definition_path: str               # Example: 'resource/0/aws_s3_bucket/foo-bucket/region/0'

    # Make the object subscriptable for backwards compatibility to when a simple dict was used
    def __getitem__(self, item: str) -> str:
        if not isinstance(item, str):
            raise TypeError("Item key must be a str")

        if item == "definition_name":
            return self.definition_name
        if item == "definition_expression":
            return self.definition_expression
        if item == "definition_path":
            return self.definition_path

        raise KeyError(f"Unknown key: {item}")


@dataclass
class EvaluationContext:
    var_file: str                     # File the variable was defined in (e.g., '/tf/example.tf'
    value: Any = None                 # Example: 'us-east-1'
    definitions: list[VarReference] = field(default_factory=list)

    # Make the object subscriptable for backwards compatibility to when a simple dict was used
    def __getitem__(self, item: str) -> Any:
        if not isinstance(item, str):
            raise TypeError("Item key must be a str")

        if item == "var_file":
            return self.var_file
        if item == "value":
            return self.value
        if item == "definitions":
            return self.definitions

        raise KeyError(f"Unknown key: {item}")
