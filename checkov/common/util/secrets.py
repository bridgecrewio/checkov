from __future__ import annotations

import itertools
import logging
import re

# secret categories for use as constants
from typing import Any

from pycep.typing import ParameterAttributes, ResourceAttributes

from checkov.common.typing import _CheckResult

from checkov.common.checks.base_check import BaseCheck

from checkov.common.models.enums import CheckCategories, CheckResult

AWS = 'aws'
AZURE = 'azure'
GCP = 'gcp'
GENERAL = 'general'
ALL = 'all'

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

_hash_patterns = list(map(lambda regex: re.compile(regex, re.IGNORECASE), ['^[a-f0-9]{32}$', '^[a-f0-9]{40}$']))


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

    # set a default if no category is provided; or, if categories were provided and they include 'all', then just set it
    # explicitly so we don't do any duplication
    if not categories or "all" in categories:
        categories = ("all",)

    if is_hash(s):
        return False

    for c in categories:
        if any([pattern.search(s) for pattern in _patterns[c]]):
            return True
    return False


def omit_multiple_secret_values_from_line(secrets: list[str], line_text: str) -> str:
    censored_line = line_text
    for secret in secrets:
        censored_line = omit_secret_value_from_line(secret, censored_line)
    return censored_line


def omit_secret_value_from_line(secret: str, line_text: str) -> str:
    secret_length = len(secret)
    secret_len_to_expose = secret_length // 4

    try:
        secret_index = line_text.index(secret)
    except ValueError:
        return line_text

    censored_line = f'{line_text[:secret_index + secret_len_to_expose]}' \
                    f'{"*" * (secret_length - secret_len_to_expose)}' \
                    f'{line_text[secret_index + secret_length:]}'
    return censored_line


def omit_secret_value_from_checks(check: BaseCheck, check_result: dict[str, CheckResult] | _CheckResult,
                                  entity_code_lines: list[tuple[int, str]],
                                  entity_config: dict[str, Any] | ParameterAttributes | ResourceAttributes) -> \
        list[tuple[int, str]]:
    if CheckCategories.SECRETS in check.categories and check_result.get('result') == CheckResult.FAILED:
        censored_code_lines = []
        secrets = [str(secret) for key, secret in entity_config.items() if key.startswith(f'{check.id}_secret')]
        if not secrets:
            logging.debug(f"Secret was not saved in {check.id}, can't omit")
            return entity_code_lines

        for idx, line in entity_code_lines:
            censored_line = omit_multiple_secret_values_from_line(secrets, line)
            censored_code_lines.append((idx, censored_line))
    else:
        censored_code_lines = entity_code_lines

    return censored_code_lines


def get_secrets_from_string(s: str, *categories: str) -> list[str]:
    # set a default if no category is provided; or, if categories were provided and they include 'all', then just set it
    # explicitly so we don't do any duplication
    if not categories or "all" in categories:
        categories = ("all",)

    if is_hash(s):
        return list()

    secrets: list[str] = []
    for c in categories:
        matches: list[str] = []
        for pattern in _patterns[c]:
            _matches = re.finditer(pattern, s)
            matches.extend([str(match.group()) for match in _matches])
        if matches:
            secrets.extend(matches)
    return secrets
