# flake8: noqa

# skip this file from pylint since it vulnerable by design
import json
import os

stream = os.popen('id')
output = stream.read()
result = {"result": output}

print(json.dumps(result))
