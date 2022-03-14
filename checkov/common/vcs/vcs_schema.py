import logging

import jsonschema
from jsonschema import validate


class VCSSchema():
    def __init__(self, schema) -> None:
        self.schema = schema

    def validate(self, data) -> bool:
        try:
            validate(instance=data, schema=self.schema)
        except jsonschema.exceptions.ValidationError:
            logging.debug("validation error", exc_info=True)
            return False
        return True
