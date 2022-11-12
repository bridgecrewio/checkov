from __future__ import annotations

import json
import re
from typing import Generator
from typing import Any
from typing import TYPE_CHECKING
from typing import Pattern

from detect_secrets.plugins.high_entropy_strings import Base64HighEntropyString
from detect_secrets.plugins.high_entropy_strings import HexHighEntropyString
from detect_secrets.plugins.keyword import KeywordDetector
from detect_secrets.plugins.keyword import DENYLIST
from detect_secrets.plugins.keyword import AFFIX_REGEX
from detect_secrets.plugins.keyword import CLOSING
from detect_secrets.plugins.keyword import OPTIONAL_WHITESPACE
from detect_secrets.plugins.keyword import QUOTE
from detect_secrets.plugins.keyword import SECRET
from detect_secrets.plugins.base import BasePlugin
from detect_secrets.util.filetype import FileType
from detect_secrets.util.filetype import determine_file_type

from checkov.secrets.runner import SOURCE_CODE_EXTENSION
from checkov.common.parsers.multiline_parser import BaseMultiLineParser
from checkov.common.parsers.yaml.multiline_parser import yml_multiline_parser
from checkov.common.parsers.json.multiline_parser import json_multiline_parser

if TYPE_CHECKING:
    from detect_secrets.core.potential_secret import PotentialSecret
    from detect_secrets.util.code_snippet import CodeSnippet

MAX_LINE_LENGTH = 10000
MAX_KEYWORD_LIMIT = 500
ENTROPY_KEYWORD_COMBINATOR_LIMIT = 3
ENTROPY_KEYWORD_LIMIT = 4.5


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


REGEX_VALUE_KEYWORD_BY_FILETYPE = {
    FileType.YAML: YML_PAIR_VALUE_KEYWORD_REGEX_TO_GROUP,
    FileType.JSON: JSON_PAIR_VALUE_KEYWORD_REGEX_TO_GROUP,
}

REGEX_VALUE_SECRET_BY_FILETYPE = {
    FileType.YAML: YML_PAIR_VALUE_SECRET_REGEX_TO_GROUP,
    FileType.JSON: JSON_PAIR_VALUE_SECRET_REGEX_TO_GROUP,
}

MULTILINE_PARSERS = {
    FileType.YAML: yml_multiline_parser,
    FileType.JSON: json_multiline_parser,
}


class EntropyKeywordCombinator(BasePlugin):
    secret_type = ""  # nosec  # noqa: CCE003  # a static attribute

    def __init__(self, limit: float = ENTROPY_KEYWORD_LIMIT) -> None:
        iac_limit = ENTROPY_KEYWORD_COMBINATOR_LIMIT
        self.high_entropy_scanners_iac = (Base64HighEntropyString(limit=iac_limit), HexHighEntropyString(limit=iac_limit))
        self.high_entropy_scanners = (Base64HighEntropyString(limit=limit), HexHighEntropyString(limit=limit))
        self.keyword_scanner = KeywordDetector()

    def analyze_string(self, string: str) -> Generator[str, None, None]:
        yield ""

    def analyze_line(
            self,
            filename: str,
            line: str,
            line_number: int = 0,
            context: CodeSnippet | None = None,
            raw_context: CodeSnippet | None = None,
            **kwargs: Any,
    ) -> set[PotentialSecret]:
        is_iac = f".{filename.split('.')[-1]}" not in SOURCE_CODE_EXTENSION
        filetype = determine_file_type(filename)
        multiline_parser = MULTILINE_PARSERS.get(filetype)

        if len(line) <= MAX_LINE_LENGTH:
            if is_iac:
                # classic key-value pair
                keyword_on_key = self.keyword_scanner.analyze_line(filename, line, line_number, **kwargs)
                if keyword_on_key:
                    return self.detect_secret(
                        scanners=self.high_entropy_scanners_iac,
                        filename=filename,
                        line=line,
                        line_number=line_number,
                        kwargs=kwargs
                    )

                # not so classic key-value pair, from multiline, that is only in an array format.
                # The scan is one-way backwards, so no duplicates expected.
                elif multiline_parser:
                    value_keyword_regex_to_group = REGEX_VALUE_KEYWORD_BY_FILETYPE.get(filetype)
                    secret_keyword_regex_to_group = REGEX_VALUE_SECRET_BY_FILETYPE.get(filetype)
                    return self.analyze_multiline(
                        filename=filename,
                        line=line,
                        multiline_parser=multiline_parser,
                        line_number=line_number,
                        context=context,
                        raw_context=raw_context,
                        value_pattern=value_keyword_regex_to_group,
                        secret_pattern=secret_keyword_regex_to_group,
                        kwargs=kwargs
                    )
            else:
                return self.detect_secret(
                    scanners=self.high_entropy_scanners,
                    filename=filename,
                    line=line,
                    line_number=line_number,
                    kwargs=kwargs
                )
        return set()

    def analyze_multiline(
            self,
            filename: str,
            line: str,
            multiline_parser: BaseMultiLineParser,
            line_number: int = 0,
            context: CodeSnippet | None = None,
            raw_context: CodeSnippet | None = None,
            value_pattern: dict[Pattern[str], int] | None = None,
            secret_pattern: dict[Pattern[str], int] | None = None,
            **kwargs: Any,
    ) -> set[PotentialSecret]:
        secrets: set[PotentialSecret] = set()
        if context is None or raw_context is None:
            return secrets
        value_secrets = self.extract_from_string(pattern=secret_pattern, string=context.target_line)
        for possible_secret in value_secrets:
            secret_adjust = self.format_reducing_noise_secret(possible_secret)

            entropy_on_value = self.detect_secret(
                scanners=self.high_entropy_scanners,
                filename=filename,
                line=secret_adjust,
                line_number=line_number,
                kwargs=kwargs
            )

            if entropy_on_value:
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
                    if self.extract_from_string(pattern=value_pattern, string=other_value):
                        secrets |= entropy_on_value
                        break
        return secrets

    @staticmethod
    def format_reducing_noise_secret(string: str) -> str:
        return json.dumps(string)

    @staticmethod
    def extract_from_string(pattern: dict[Pattern[str], int] | None, string: str) -> set[str]:
        matches: set[str] = set()
        if not pattern:
            return matches
        for value_regex, group_number in pattern.items():
            match = value_regex.search(string)
            if match:
                matches |= {match.group(group_number)}
        return matches

    @staticmethod
    def detect_secret(
            scanners: tuple[Base64HighEntropyString, HexHighEntropyString],
            filename: str,
            line: str,
            line_number: int = 0,
            **kwargs: Any,
    ) -> set[PotentialSecret]:
        for entropy_scanner in scanners:
            matches = entropy_scanner.analyze_line(filename, line, line_number, **kwargs)
            if matches:
                return matches
        return set()
