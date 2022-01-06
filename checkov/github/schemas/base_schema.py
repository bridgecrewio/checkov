import jsonschema
from jsonschema import validate


class GithubConfSchema():
    def __init__(self, schema):
        self.schema = schema

    def validate(self, data):
        try:
            validate(instance=data, schema=self.schema)
        except jsonschema.exceptions.ValidationError as err:
            return False
        return True
