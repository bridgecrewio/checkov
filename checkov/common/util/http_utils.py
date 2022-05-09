from __future__ import annotations

import json
import requests
import logging
import time
import os
from typing import Any, TYPE_CHECKING, cast

from checkov.common.bridgecrew.bc_source import SourceType
from checkov.common.util.consts import DEV_API_GET_HEADERS, DEV_API_POST_HEADERS
from checkov.common.util.data_structures_utils import merge_dicts
from checkov.version import version as checkov_version

if TYPE_CHECKING:
    from requests import Response


logger = logging.getLogger(__name__)


def normalize_prisma_url(url: str) -> str | None:
    """ Correct common Prisma Cloud API URL misconfigurations """
    if not url:
        return None
    return url.lower().replace('//app', '//api').replace('http:', 'https:').rstrip('/')


def extract_error_message(response: requests.Response) -> str:
    if response.content:
        try:
            content = json.loads(response.content)
            if 'message' in content:
                return cast(str, content['message'])
        except Exception:
            logging.debug(f'Failed to parse the response content: {response.content.decode()}')

    return response.reason


def get_auth_header(token: str) -> dict[str, str]:
    return {
        'Authorization': token
    }


def get_version_headers(client: str, client_version: str) -> dict[str, str]:
    return {
        'x-api-client': client,
        'x-api-version': client_version,
        'x-api-checkov-version': checkov_version
    }


def get_user_agent_header() -> dict[str, str]:
    return {'User-Agent': f'checkov/{checkov_version}'}


def get_default_get_headers(client: SourceType, client_version: str) -> dict[str, Any]:
    return merge_dicts(DEV_API_GET_HEADERS, get_version_headers(client.name, client_version), get_user_agent_header())


def get_default_post_headers(client: SourceType, client_version: str) -> dict[str, Any]:
    return merge_dicts(DEV_API_POST_HEADERS, get_version_headers(client.name, client_version), get_user_agent_header())


def request_wrapper(
    method: str,
    url: str,
    headers: dict[str, Any],
    data: Any | None = None,
    json: dict[str, Any] | None = None,
    should_call_raise_for_status: bool = False
) -> Response | None:
    # using of "retry" mechanism for 'requests.request' due to unpredictable 'ConnectionError' and 'HttpError'
    # instances that appears from time to time.
    # 'ConnectionError' instances that appeared:
    # * 'Connection aborted.', ConnectionResetError(104, 'Connection reset by peer').
    # * 'Connection aborted.', OSError(107, 'Socket not connected').
    # 'ConnectionError' instances that appeared:
    # * 403 Client Error: Forbidden for url.
    # * 504 Server Error: Gateway Time-out for url.

    request_max_tries = int(os.getenv('REQUEST_MAX_TRIES', 3))
    sleep_between_request_tries = float(os.getenv('SLEEP_BETWEEN_REQUEST_TRIES', 1))

    for i in range(request_max_tries):
        try:
            response = requests.request(method, url, headers=headers, data=data, json=json)
            if should_call_raise_for_status:
                response.raise_for_status()
            return response
        except requests.exceptions.ConnectionError as connection_error:
            logging.error(f"Connection error on request {method}:{url},\ndata:\n{data}\njson:{json}\nheaders:{headers}")
            if i != request_max_tries - 1:
                time.sleep(sleep_between_request_tries * (i + 1))
                continue
            raise connection_error
        except requests.exceptions.HTTPError as http_error:
            logging.error(f"HTTP error on request {method}:{url},\ndata:\n{data}\njson:{json}\nheaders:{headers}")
            status_code = http_error.response.status_code
            if (status_code >= 500 or status_code == 403) and i != request_max_tries - 1:
                time.sleep(sleep_between_request_tries * (i + 1))
                continue
            raise http_error

    return None
