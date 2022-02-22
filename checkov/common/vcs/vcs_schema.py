import logging

import jsonschema
from jsonschema import validate


class VCSSchema():
    def __init__(self, schema):
        self.schema = schema

    def validate(self, data):
        try:
            validate(instance=data, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            logging.debug("validation error {}", e)
            return False
        return True
