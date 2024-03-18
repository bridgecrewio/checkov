from __future__ import annotations

import json
import re
from re import Pattern
from typing import Any, TYPE_CHECKING, Optional

from detect_secrets.util.filetype import FileType
from detect_secrets.plugins.keyword import DENYLIST
from detect_secrets.plugins.keyword import AFFIX_REGEX
from detect_secrets.plugins.keyword import CLOSING
from detect_secrets.plugins.keyword import OPTIONAL_WHITESPACE
from detect_secrets.plugins.keyword import QUOTE
from detect_secrets.plugins.keyword import SECRET

from checkov.secrets.parsers.terraform.multiline_parser import terraform_multiline_parser
from checkov.secrets.parsers.terraform.single_line_parser import terraform_single_line_parser
from checkov.secrets.parsers.yaml.multiline_parser import yml_multiline_parser
from checkov.secrets.parsers.json.multiline_parser import json_multiline_parser

if TYPE_CHECKING:
    from checkov.secrets.parsers.multiline_parser import BaseMultiLineParser
    from detect_secrets.core.potential_secret import PotentialSecret
    from detect_secrets.util.code_snippet import CodeSnippet
    from detect_secrets.plugins.base import BasePlugin

MAX_KEYWORD_LIMIT = 500

DENY_LIST_REGEX = r'|'.join(DENYLIST)
# Support for suffix after keyword i.e. password_secure = "value"
DENY_LIST_REGEX2 = r'({denylist}){suffix}'.format(
    denylist=DENY_LIST_REGEX,
    suffix=AFFIX_REGEX,
)

KEY = r'{words}({closing})?'.format(
    words=AFFIX_REGEX,
    closing=CLOSING,
)

FOLLOWED_BY_COLON_VALUE_KEYWORD_REGEX = re.compile(
    # e.g. var: MY_PASSWORD_123
    r'{whitespace}({key})?:{whitespace}({quote}?){words}{denylist}({closing})?(\3)'.format(
        key=KEY,
        whitespace=OPTIONAL_WHITESPACE,
        quote=QUOTE,
        words=AFFIX_REGEX,
        denylist=DENY_LIST_REGEX2,
        closing=CLOSING,
    ),
    flags=re.IGNORECASE,
)

QUOTES_REQUIRED_FOLLOWED_BY_COLON_VALUE_KEYWORD_REGEX = re.compile(
    # e.g. var: MY_PASSWORD_123
    r'{whitespace}"({key})?":{whitespace}("?){words}{denylist}({closing})?(\3)'.format(
        key=KEY,
        whitespace=OPTIONAL_WHITESPACE,
        words=AFFIX_REGEX,
        denylist=DENY_LIST_REGEX2,
        closing=CLOSING,
    ),
    flags=re.IGNORECASE,
)

FOLLOWED_BY_COLON_VALUE_SECRET_REGEX = re.compile(
    # e.g. var: Zmlyc3Rfc2VjcmV0X2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzE==
    r'{whitespace}({key})?:{whitespace}({quote}?)({secret})(\3)'.format(
        key=KEY,
        whitespace=OPTIONAL_WHITESPACE,
        quote=QUOTE,
        secret=SECRET,
    ),
    flags=re.IGNORECASE,
)

QUOTES_REQUIRED_FOLLOWED_BY_COLON_VALUE_SECRET_REGEX = re.compile(
    # e.g. var: Zmlyc3Rfc2VjcmV0X2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzE==
    r'{whitespace}"({key})?":{whitespace}("?)({secret})(\3)'.format(
        key=KEY,
        whitespace=OPTIONAL_WHITESPACE,
        secret=SECRET,
    ),
    flags=re.IGNORECASE,
)

FOLLOWED_BY_EQUAL_VALUE_KEYWORD_REGEX = re.compile(
    # e.g. var = MY_PASSWORD_123
    r'{whitespace}({key})?={whitespace}({quote}?){words}{denylist}({closing})?(\3)'.format(
        key=KEY,
        whitespace=OPTIONAL_WHITESPACE,
        quote=QUOTE,
        words=AFFIX_REGEX,
        denylist=DENY_LIST_REGEX2,
        closing=CLOSING,
    ),
    flags=re.IGNORECASE,
)

FOLLOWED_BY_EQUAL_VALUE_SECRET_REGEX = re.compile(
    # e.g. var = Zmlyc3Rfc2VjcmV0X2hlcmVfd2hvYV9tdWx0aWxsaW5lX3Nob3VsZF93b3JrXzE==
    r'{whitespace}({key})?={whitespace}({quote}?)({secret})(\3)'.format(
        key=KEY,
        whitespace=OPTIONAL_WHITESPACE,
        quote=QUOTE,
        secret=SECRET,
    ),
    flags=re.IGNORECASE,
)

ALLOW_LIST = (  # can add more keys like that
    'secretsmanager',
    "secretName",
    "secret_name",
    "creation_token",
    "client_secret_setting_name",
)
ALLOW_LIST_REGEX = r'|'.join(ALLOW_LIST)
# Support for suffix of function name i.e "secretsmanager:GetSecretValue"
CAMEL_CASE_NAMES = r'[A-Z]([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|[a-z0-9]*[A-Z][A-Z0-9]*[a-z])[A-Za-z0-9]*'
FUNCTION_CALL_AFTER_KEYWORD_REGEX = re.compile(r'({allowlist})\s*(:|=)\s*{suffix}'.format(
    allowlist=ALLOW_LIST_REGEX,
    suffix=AFFIX_REGEX,
))

#  if the current regex is not enough, can add more regexes to check

YML_PAIR_VALUE_KEYWORD_REGEX_TO_GROUP = {
    FOLLOWED_BY_COLON_VALUE_KEYWORD_REGEX: 4,
}

YML_PAIR_VALUE_SECRET_REGEX_TO_GROUP = {
    FOLLOWED_BY_COLON_VALUE_SECRET_REGEX: 4,
}

JSON_PAIR_VALUE_KEYWORD_REGEX_TO_GROUP = {
    QUOTES_REQUIRED_FOLLOWED_BY_COLON_VALUE_KEYWORD_REGEX: 4,
}

JSON_PAIR_VALUE_SECRET_REGEX_TO_GROUP = {
    QUOTES_REQUIRED_FOLLOWED_BY_COLON_VALUE_SECRET_REGEX: 4,
}

TERRAFORM_PAIR_VALUE_KEYWORD_REGEX_TO_GROUP = {
    FOLLOWED_BY_EQUAL_VALUE_KEYWORD_REGEX: 4,
}

TERRAFORM_PAIR_VALUE_SECRET_REGEX_TO_GROUP = {
    FOLLOWED_BY_EQUAL_VALUE_SECRET_REGEX: 4,
}

REGEX_VALUE_KEYWORD_BY_FILETYPE = {
    FileType.YAML: YML_PAIR_VALUE_KEYWORD_REGEX_TO_GROUP,
    FileType.JSON: JSON_PAIR_VALUE_KEYWORD_REGEX_TO_GROUP,
    FileType.TERRAFORM: TERRAFORM_PAIR_VALUE_KEYWORD_REGEX_TO_GROUP,
}

REGEX_VALUE_SECRET_BY_FILETYPE = {
    FileType.YAML: YML_PAIR_VALUE_SECRET_REGEX_TO_GROUP,
    FileType.JSON: JSON_PAIR_VALUE_SECRET_REGEX_TO_GROUP,
    FileType.TERRAFORM: TERRAFORM_PAIR_VALUE_SECRET_REGEX_TO_GROUP,
}

SINGLE_LINE_PARSER = {
    FileType.TERRAFORM: terraform_single_line_parser,
}

MULTILINE_PARSERS = {
    FileType.YAML: (
        (FileType.YAML, yml_multiline_parser),
    ),
    FileType.JSON: (
        (FileType.JSON, json_multiline_parser),
    ),
    FileType.TERRAFORM: (
        (FileType.TERRAFORM, terraform_multiline_parser),
        (FileType.JSON, json_multiline_parser),
        (FileType.YAML, yml_multiline_parser),
    ),
}


def remove_fp_secrets_in_keys(detected_secrets: set[PotentialSecret], line: str, is_code_file: bool = False) -> None:
    formatted_line = line.replace('"', '').replace("'", '')
    secrets_to_remove = set()
    for detected_secret in detected_secrets:
        if not detected_secret.secret_value:
            continue
        processed_line = get_processed_line(formatted_line, detected_secret.secret_value)
        # Found keyword prefix as potential secret
        if processed_line.startswith(detected_secret.secret_value):
            secrets_to_remove.add(detected_secret)
        # found a function name at the end of the line
        if processed_line and FUNCTION_CALL_AFTER_KEYWORD_REGEX.search(processed_line):
            secrets_to_remove.add(detected_secret)
        # secret value is substring of keywork
        if is_code_file and FOLLOWED_BY_EQUAL_VALUE_KEYWORD_REGEX.search(processed_line):
            key, value = line.split("=", 1)
            if detected_secret.secret_value in key and detected_secret.secret_value in value:
                secrets_to_remove.add(detected_secret)
    detected_secrets -= secrets_to_remove


def get_processed_line(formatted_line: str, secret_value: str) -> str:
    if not formatted_line.startswith(secret_value) and formatted_line.find(":", formatted_line.rfind(secret_value) + len(secret_value)) > -1:
        return formatted_line[formatted_line.find(secret_value):]
    return formatted_line


def format_reducing_noise_secret(string: str) -> str:
    return json.dumps(string)


def extract_from_string(pattern: dict[Pattern[str], int] | None, string: str) -> set[str]:
    matches: set[str] = set()
    if not pattern:
        return matches
    for value_regex, group_number in pattern.items():
        match = value_regex.search(string)
        if match:
            matches |= {match.group(group_number).rstrip('\n')}
    return matches


def detect_secret(
        scanners: tuple[BasePlugin, ...],
        filename: str,
        line: str,
        line_number: int = 0,
        is_multiline: Optional[bool] = None,
        **kwargs: Any,
) -> set[PotentialSecret]:
    for scanner in scanners:
        matches = scanner.analyze_line(filename, line, line_number, **kwargs)
        if matches:
            if is_multiline:
                mark_set_multiline(matches)
            return matches
    return set()


def analyze_multiline_keyword_combinator(
        filename: str,
        scanners: tuple[BasePlugin, ...],
        multiline_parser: BaseMultiLineParser,
        line_number: int,
        context: CodeSnippet | None = None,
        raw_context: CodeSnippet | None = None,
        value_pattern: dict[Pattern[str], int] | None = None,
        secret_pattern: dict[Pattern[str], int] | None = None,
        is_added: bool = False,
        is_removed: bool = False,
        **kwargs: Any,
) -> set[PotentialSecret]:
    secrets: set[PotentialSecret] = set()
    if context is None or raw_context is None:
        return secrets
    value_secrets = extract_from_string(pattern=secret_pattern, string=context.target_line)
    for possible_secret in value_secrets:
        secret_adjust = format_reducing_noise_secret(possible_secret)

        potential_secrets = detect_secret(
            scanners=scanners,
            filename=filename,
            line=secret_adjust,
            line_number=line_number,
            is_added=is_added,
            is_removed=is_removed,
            is_multiline=True,  # always true because we check here for multiline
            kwargs=kwargs
        )

        if potential_secrets:
            possible_keywords: set[str] = set()
            backwards_range = range(context.target_index - 1, -1, -1)
            forward_range = range(context.target_index + 1, len(context.lines))

            possible_keywords |= multiline_parser.get_lines_from_same_object(
                search_range=forward_range,
                context=context,
                raw_context=raw_context,
                line_length_limit=MAX_KEYWORD_LIMIT)
            possible_keywords |= multiline_parser.get_lines_from_same_object(
                search_range=backwards_range,
                context=context,
                raw_context=raw_context,
                line_length_limit=MAX_KEYWORD_LIMIT)

            for other_value in possible_keywords:
                if extract_from_string(pattern=value_pattern, string=other_value):
                    secrets |= potential_secrets
                    break
    return secrets


def mark_set_multiline(secrets: set[PotentialSecret]) -> None:
    for sec in secrets:
        sec.is_multiline = True
