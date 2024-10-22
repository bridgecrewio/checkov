from __future__ import annotations

import logging
from typing import Any

import jsonschema
from jsonschema import validate


class VCSSchema():
    def __init__(self, schema: dict[str, Any]) -> None:
        self.schema = schema

    def validate(self, data: dict[str, Any] | list[dict[str, Any]]) -> bool:
        try:
            validate(instance=data, schema=self.schema)
        except jsonschema.exceptions.ValidationError:
            logging.debug("validation error", exc_info=True)
            return False
        return True
