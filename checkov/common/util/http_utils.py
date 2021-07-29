import json
import requests
import logging

from checkov.common.bridgecrew.bc_source import SourceType
from checkov.common.util.consts import DEV_API_GET_HEADERS, DEV_API_POST_HEADERS
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.version import version as checkov_version

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


def get_auth_header(token):
    return {
        'Authorization': token
    }


def get_version_headers(client, client_version):
    return {
        'x-api-client': client,
        'x-api-version': client_version,
        'x-api-checkov-version': checkov_version
    }


def get_default_get_headers(client: SourceType, client_version: str):
    return merge_dicts(DEV_API_GET_HEADERS, get_version_headers(client.name, client_version))


def get_default_post_headers(client: SourceType, client_version: str):
    return merge_dicts(DEV_API_POST_HEADERS, get_version_headers(client.name, client_version))