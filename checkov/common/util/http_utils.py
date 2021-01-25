import json
import requests
import logging

logger = logging.getLogger(__name__)


def extract_error_message(response: requests.Response):
    if response.content:
        try:
            content = json.loads(response.content)
            if 'message' in content:
                return content['message']
        except:
            logging.debug(f'Failed to parse the response content: {response.content}')

    return response.reason
