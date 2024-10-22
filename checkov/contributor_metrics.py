from __future__ import annotations

import datetime
import logging
import json
import subprocess  # nosec

from checkov.common.resource_code_logger_filter import add_resource_code_filter_to_logger
from checkov.common.util.http_utils import request_wrapper
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from typing import Any

logger = logging.getLogger(__name__)
add_resource_code_filter_to_logger(logger)


def report_contributor_metrics(repository: str, source: str,
                               bc_integration: BcPlatformIntegration) -> None:  # ignore: type
    logging.debug(f"Attempting to get log history for repository {repository} under source {source}")
    request_body = parse_gitlog(repository, source)
    number_of_attempts = 1
    contributors_report_api_url = f"{bc_integration.api_url}/api/v2/contributors/report"
    if request_body:
        while number_of_attempts <= 4:
            logging.debug(f'Uploading contributor metrics to {contributors_report_api_url}')
            response = request_wrapper(
                "POST", contributors_report_api_url,
                headers=bc_integration.get_default_headers("POST"), data=json.dumps(request_body)
            )
            logging.debug(f'Request ID: {response.headers.get("x-amzn-requestid")}')
            logging.debug(f'Trace ID: {response.headers.get("x-amzn-trace-id")}')
            if response.status_code < 300:
                logging.debug(
                    f"Successfully uploaded contributor metrics with status: {response.status_code}. number of attempts: {number_of_attempts}")
                break
            else:
                contributors_report_api_url = f"{bc_integration.api_url}/api/v1/contributors/report"
                failed_attempt = {
                    'message': f"Failed to upload contributor metrics with: {response.status_code} - {response.reason}. number of attempts: {number_of_attempts}",
                    'timestamp': str(datetime.datetime.now())}
                request_body['failedAttempts'].append(failed_attempt)
                logging.info(f"Failed to upload contributor metrics with: {response.status_code} - {response.reason}")
                number_of_attempts += 1


def parse_gitlog(repository: str, source: str) -> dict[str, Any] | None:
    process = subprocess.Popen(['git', 'shortlog', '-ne', '--all', '--since', '"90 days ago"', '--pretty=commit-%ct', '--reverse'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
    out, err = process.communicate()
    if err:
        logger.info(f"Failed to collect contributor metrics due to: {err}")  # type: ignore
        return {"repository": repository, "source": source,
                "contributors": [],
                "failedAttempts": [{
                    'message': f"Failed to collect contributor metrics due to: {err}",  # type: ignore
                    'timestamp': str(datetime.datetime.now())}]
                }
    # split per contributor
    list_of_contributors = out.decode('utf-8').split('\n\n')
    return {"repository": repository, "source": source,
            "contributors": list(map(lambda contributor: process_contributor(contributor),
                                     list(filter(lambda x: x, list_of_contributors))
                                     )),
            "failedAttempts": []
            }


def process_contributor(contributor: str) -> str:
    splittedList = contributor.split('\n')
    user = splittedList[0]
    commit = splittedList[1]
    return user[:user.find('(')] + commit[commit.find('-') + 1:]
