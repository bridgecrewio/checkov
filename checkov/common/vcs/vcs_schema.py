import jsonschema
from jsonschema import validate


class VCSSchema():
    def __init__(self, schema):
        self.schema = schema

    def validate(self, data):
        try:
            validate(instance=data, schema=self.schema)
        except jsonschema.exceptions.ValidationError:
            return False
        return True
