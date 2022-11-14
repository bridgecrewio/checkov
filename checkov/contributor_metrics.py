from __future__ import annotations
import logging
import json
import subprocess  # nosec
from checkov.common.util.http_utils import request_wrapper
from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from typing import Any

logger = logging.getLogger(__name__)


def report_contributor_metrics(repository: str, bc_integration: BcPlatformIntegration) -> None:  # ignore: type
    logging.debug(f"Attempting to get log history for repository {repository}")
    request_body = parse_gitlog(repository)
    if request_body:
        response = request_wrapper(
            "POST", f"{bc_integration.api_url}/api/v1/contributors/report",
            headers=bc_integration.get_default_headers("POST"), data=json.dumps(request_body)
        )
        if response.status_code < 300:
            logging.info(f"Successfully uploaded contributor metrics with status: {response.status_code}")
        else:
            logging.info(f"Failed to upload contributor metrics with: {response.status_code} - {response.reason}")


def parse_gitlog(repository: str) -> dict[str, Any] | None:
    process = subprocess.Popen(['git', 'shortlog', '-ne', '--all', '--since', '"90 days ago"', '--pretty=commit-%ct', '--reverse'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
    out, err = process.communicate()
    if err:
        logger.info(f"Failed to collect contributor metrics due to: {err}")     # type: ignore
        return None
    # split per contributor
    list_of_contributors = out.decode('utf-8').split('\n\n')
    return {"repository": repository,
            "contributors": list(map(lambda contributor: process_contributor(contributor),
                                     list(filter(lambda x: x, list_of_contributors))
                                     ))
            }


def process_contributor(contributor: str) -> str:
    splittedList = contributor.split('\n')
    user = splittedList[0]
    commit = splittedList[1]
    return user[:user.find('(')] + commit[commit.find('-') + 1:]
