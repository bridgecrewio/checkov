import json
import requests


def extract_error_message(response: requests.Response):
    if response.content:
        try:
            content = json.loads(response.content)
            if 'message' in content:
                return content['message']
        except:
            pass

    return response.reason