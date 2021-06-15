import json


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return json.JSONEncoder.default(self, list(o))
        else:
            return json.JSONEncoder.default(self, o)
