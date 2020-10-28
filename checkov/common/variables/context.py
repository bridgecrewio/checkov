from dataclasses import dataclass
from typing import List, Tuple, Any


# NOTE: These would be better as TypedDict, but that requires python 3.8 :-(


# EntityContext defines the code-level context for a particular entity: line number range, the actual code
# and any checks that should be skipped.
@dataclass
class EntityContext:
    start_line: int
    end_line: int
    code_lines: List[Tuple[int, str]]
    skipped_checks: List[str]

    # Make the object subscriptable for backwards compatibility to when a simple dict was used
    def __getitem__(self, item):
        if not isinstance(item, str):
            raise TypeError("Item key must be a str")

        if item == "start_line":
            return self.start_line
        if item == "end_line":
            return self.end_line
        if item == "code_lines":
            return self.code_lines
        if item == "skipped_checks":
            return self.skipped_checks

        raise KeyError(f"Unknown key: {item}")


@dataclass
class VarReference:
    expression: str         # Example: '${var.region}'
    path: str               # Example: 'resource/0/aws_s3_bucket/foo-bucket/region/0'

    # Make the object subscriptable for backwards compatibility to when a simple dict was used
    def __getitem__(self, item):
        if not isinstance(item, str):
            raise TypeError("Item key must be a str")

        if item == "definition_expression" or item == "expression":
            return self.expression
        if item == "definition_path" or item == "path":
            return self.path

        raise KeyError(f"Unknown key: {item}")


@dataclass
class EvaluationContext:
    var_file: str                       # Example: '/tf/example.tf'
    value: Any                          # Example: 'us-east-1'
    definitions: List[VarReference]

    # Make the object subscriptable for backwards compatibility to when a simple dict was used
    def __getitem__(self, item):
        if not isinstance(item, str):
            raise TypeError("Item key must be a str")

        if item == "var_file":
            return self.var_file
        if item == "value":
            return self.value
        if item == "definitions":
            return self.definitions

        raise KeyError(f"Unknown key: {item}")
