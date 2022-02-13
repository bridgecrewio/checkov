import json
import os

stream = os.popen('id')
output = stream.read()
result = { "result" : output }

print(json.dumps(result))