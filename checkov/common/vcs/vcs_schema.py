from typing import Dict, Any
import jsonschema
from jsonschema import validate


class VCSSchema():
    def __init__(self, schema: Dict[str, Any]) -> None:
        self.schema = schema

    def validate(self, data: Dict[str, Any]) -> bool:
        try:
            validate(instance=data, schema=self.schema)
        except jsonschema.exceptions.ValidationError:
            return False
        return True
