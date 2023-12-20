from __future__ import annotations

import itertools
import json
import logging
import re
from typing import Any, TYPE_CHECKING

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.util.consts import RESOURCE_ATTRIBUTES_TO_OMIT_UNIVERSAL_MASK

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.graph.checks_infra.base_check import BaseGraphCheck
    from checkov.common.typing import _CheckResult, ResourceAttributesToOmit
    from pycep.typing import ParameterAttributes, ResourceAttributes

# secret categories for use as constants
AWS = 'aws'
AZURE = 'azure'
GCP = 'gcp'
GENERAL = 'general'
ALL = 'all'

GENERIC_OBFUSCATION_LENGTH = 10


# Taken from various git-secrets forks that add Azure and GCP support to base AWS.
# The groups here are the result of running git secrets --register-[aws|azure|gcp]
# https://github.com/awslabs/git-secrets
# https://github.com/deshpandetanmay/git-secrets
# https://github.com/msalemcode/git-secrets#options-for-register-azure
_secrets_regexes = {
    'azure': [
        "(\"|')?([0-9A-Fa-f]{4}-){4}[0-9A-Fa-f]{12}(\"|')?",  # client_secret
        "(\"|')?[0-9A-Fa-f]{8}-([0-9A-Fa-f]{4}-){3}[0-9A-Fa-f]{12}(\"|')?",  # client_id and many other forms of IDs
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][o|O][n|N][m|M][i|I][c|C][r|R][o|O][s|S][o|O][f|F][t|T][.][c|C][o|O][m|M](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][b|B][l|L][o|O][b|B][.][c|C][o|O][r|R][e|E][.][w|W][i|I][n|N][d|D][o|O][w|W][s|S][.][n|N][e|E][t|T](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][q|Q][u|U][e|E][u|U][e|E][.][c|C][o|O][r|R][e|E][.][w|W][i|I][n|N][d|D][o|O][w|W][s|S][.][n|N][e|E][t|T](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][t|T][a|A][b|B][l|L][e|E][.][c|C][o|O][r|R][e|E][.][w|W][i|I][n|N][d|D][o|O][w|W][s|S][.][n|N][e|E][t|T](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][d|D][a|A][t|T][a|A][b|B][a|A][s|S][e|E][.][w|W][i|I][n|N][d|D][o|O][w|W][s|S][.][n|N][e|E][t|T](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][s|S][e|E][r|R][v|V][i|I][c|C][e|E][b|B][u|U][s|S][.][w|W][i|I][n|N][d|D][o|O][w|W][s|S][.][n|N][e|E][t|T](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][t|T][i|I][m|M][e|E][s|S][e|E][r|R][i|I][e|E][s|S][.][a|A][z|Z][u|U][r|R][e|E][.][c|C][o|O][m|M](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][a|T][c|C][c|C][e|E][s|S][s|S][c|C][o|O][n|N][t|T][r|R][o|O][l|L][.][w|W][i|I][n|N][d|D][o|O][w|W][s|S][.][n|N][e|E][t|T](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][a|A][z|Z][u|U][r|R][e|E][h|H][d|D][i|I][n|N][s|S][i|I][g|G][h|H][t|T][.][n|N][e|E][t|T](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][c|C][l|L][o|O][u|U][d|D][a|A][p|P][p|P][.][a|A][z|Z][u|U][r|R][e|E][.][c|C][o|O][m|M](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][c|C][l|L][o|O][u|U][d|D][a|A][p|P][p|P][.][n|N][e|E][t|T](\"|')?",
        "(\"|')?.*[0-9a-zA-Z]{2,256}[.][d|D][o|O][c|C][u|U][m|M][e|E][n|N][t|T][s|S][.][a|A][z|Z][u|U][r|R][e|E][.][c|C][o|O][m|M](\"|')?",
    ],

    'aws': [
        "(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])",  # AWS secret access key
        "(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",  # AWS access key ID
        "(\"|')?(AWS|aws|Aws)?_?(SECRET|secret|Secret)?_?(ACCESS|access|Access)?_?(KEY|key|Key)(\"|')?\\s*(:|=>|=)\\s*(\"|')?[A-Za-z0-9/\\+=]{40}(\"|')?",
        "(\"|')?(AWS|aws|Aws)?_?(ACCOUNT|account|Account)_?(ID|id|Id)?(\"|')?\\s*(:|=>|=)\\s*(\"|')?[0-9]{4}\\-?[0-9]{4}\\-?[0-9]{4}(\"|')?"
    ],

    'gcp': [
        "\bprivate_key.*\b"
    ],

    'general': [
        "^-----BEGIN (RSA|EC|DSA|GPP) PRIVATE KEY-----$",
    ]
}

# first compile each unique regex while maintaining the mapping
_patterns = {k: [re.compile(p, re.DOTALL) for p in v] for k, v in _secrets_regexes.items()}

# now combine all the compiled patterns into one long list
_patterns['all'] = list(itertools.chain.from_iterable(_patterns.values()))

_hash_patterns = [re.compile(regex, re.IGNORECASE) for regex in ('^[a-f0-9]{32}$', '^[a-f0-9]{40}$')]


def is_hash(s: str) -> bool:
    """
    Checks whether a string is a MD5 or SHA1 hash

    :param s:
    :return:
    """
    return any(pattern.search(s) for pattern in _hash_patterns)


def string_has_secrets(s: str, *categories: str) -> bool:
    """
    Check whether the specified string has any matches for the regexes in the specified category(ies).

    If categories is blank, then this method checks all categories. It is recommended to use the category constants
    provided.

    Examples:
    string_has_secrets(some_string) -> checks all regexes
    string_has_secrets(some_string, AWS, GENERAL) -> checks only AWS and general regexes.

    :param s:
    :param categories:
    :return:
    """

    if is_hash(s):
        return False

    # set a default if no category is provided; or, if categories were provided and they include 'all', then just set it
    # explicitly so we don't do any duplication
    if not categories or "all" in categories:
        categories = ("all",)

    for c in categories:
        if any([pattern.search(s) for pattern in _patterns[c]]):
            return True
    return False


def omit_multiple_secret_values_from_line(secrets: set[str], line_text: str) -> str:
    censored_line = line_text
    for secret in secrets:
        censored_line = omit_secret_value_from_line(secret, censored_line)
    return censored_line


def omit_secret_value_from_line(secret: str | None, line_text: str) -> str:
    if not secret or not isinstance(secret, str):
        return line_text

    secret_length = len(secret)
    secret_len_to_expose = min(secret_length // 4, 6)  # no more than 6 characters should be exposed

    try:
        secret_index = line_text.index(secret)
    except ValueError:
        try:
            secret_index = line_text.index(json.dumps(secret))
        except ValueError:
            return line_text

    censored_line = f'{line_text[:secret_index + secret_len_to_expose]}' \
                    f'{"*" * GENERIC_OBFUSCATION_LENGTH}' \
                    f'{line_text[secret_index + secret_length:]}'
    return censored_line


def omit_secret_value_from_checks(
        check: BaseCheck,
        check_result: dict[str, CheckResult] | _CheckResult,
        entity_code_lines: list[tuple[int, str]],
        entity_config: dict[str, Any] | ParameterAttributes | ResourceAttributes,
        resource_attributes_to_omit: ResourceAttributesToOmit | None = None
) -> list[tuple[int, str]]:
    # a set, to efficiently avoid duplicates in case the same secret is found in the following conditions
    secrets = set()
    censored_code_lines = []

    if CheckCategories.SECRETS in check.categories and check_result.get('result') == CheckResult.FAILED:
        secrets.update([str(secret) for key, secret in entity_config.items() if
                        key.startswith(f'{check.id}_secret')])

    if resource_attributes_to_omit:
        universal_mask = resource_attributes_to_omit.get(RESOURCE_ATTRIBUTES_TO_OMIT_UNIVERSAL_MASK, set())
        resource_masks = resource_attributes_to_omit.get(check.entity_type, set())
        resource_masks.update(universal_mask)
        for key, secret in entity_config.items():
            if key not in resource_masks:
                continue
            if isinstance(secret, list) and secret:
                if not isinstance(secret[0], str):
                    logging.debug(f"Secret value can't be masked, has type {type(secret)}")
                    continue

                secrets.add(secret[0])

    if not secrets:
        logging.debug(f"Secret was not saved in {check.id}, can't omit")
        return entity_code_lines

    for idx, line in entity_code_lines:
        censored_line = omit_multiple_secret_values_from_line(secrets, line)
        censored_code_lines.append((idx, censored_line))

    return censored_code_lines


def omit_secret_value_from_graph_checks(
        check: BaseGraphCheck,
        check_result: dict[str, CheckResult] | _CheckResult,
        entity_code_lines: list[tuple[int, str]],
        entity_config: dict[str, Any] | ParameterAttributes | ResourceAttributes,
        resource_attributes_to_omit: ResourceAttributesToOmit | None = None
) -> list[tuple[int, str]]:
    # a set, to efficiently avoid duplicates in case the same secret is found in the following conditions
    secrets = set()
    censored_code_lines = []

    if check.category == CheckCategories.SECRETS.name and check_result.get('result') == CheckResult.FAILED:
        secrets = {
            str(secret) for key, secret in entity_config.items()
            if key.startswith(f'{check.id}_secret')
        }

    if resource_attributes_to_omit:
        # Universal mask ('*') might exist in resource_attributes_to_omit. If it does exist, we need to mask all the
        # entities in resource types according to resource_attributes_to_omit.get('*')
        universal_mask = set(resource_attributes_to_omit.get(RESOURCE_ATTRIBUTES_TO_OMIT_UNIVERSAL_MASK, set()))
        for resource in check.resource_types:
            resource_masks = set(resource_attributes_to_omit.get(resource, set()))
            # resource_masks should contain all mask rules that should apply on this resource
            resource_masks.update(universal_mask)
            if not resource_masks:
                continue
            # If entity is one that should be masked, we add it the value to secrets
            for attribute, secret in entity_config.items():
                if attribute in resource_masks:
                    if isinstance(secret, list) and secret:
                        if not isinstance(secret[0], str):
                            logging.debug(f"Secret value can't be masked, has type {type(secret)}")
                            continue

                        secrets.add(secret[0])

    if not secrets:
        logging.debug(f"Secret was not saved in {check.id}, can't omit")
        return entity_code_lines

    for idx, line in entity_code_lines:
        censored_line = omit_multiple_secret_values_from_line(secrets, line)
        censored_code_lines.append((idx, censored_line))

    return censored_code_lines


def get_secrets_from_string(s: str, *categories: str) -> list[str]:
    # set a default if no category is provided; or, if categories were provided and they include 'all', then just set it
    # explicitly so we don't do any duplication
    if is_hash(s):
        return []

    if not categories or "all" in categories:
        categories = ("all",)

    secrets: list[str] = []
    for c in categories:
        for pattern in _patterns[c]:
            secrets.extend(str(match.group()) for match in pattern.finditer(s))
    return secrets
