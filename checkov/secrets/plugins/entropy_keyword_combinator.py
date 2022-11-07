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

if TYPE_CHECKING:
    from detect_secrets.core.potential_secret import PotentialSecret
    from detect_secrets.util.code_snippet import CodeSnippet

MAX_LINE_LENGTH = 10000
ENTROPY_KEYWORD_COMBINATOR_LIMIT = 3
ENTROPY_KEYWORD_LIMIT = 4.5

INDENTATION_PATTERN = re.compile(r'(^\s*(?:-?\s+)?)')
COMMENT_PREFIX = re.compile(r'^[\s]*(#|\/\/)')

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

PAIR_VALUE_KEYWORD_REGEX_TO_GROUP = {
    FOLLOWED_BY_COLON_VALUE_KEYWORD_REGEX: 4,
}

PAIR_VALUE_SECRET_REGEX_TO_GROUP = {
    FOLLOWED_BY_COLON_VALUE_SECRET_REGEX: 4,
}

REGEX_VALUE_KEYWORD_BY_FILETYPE = {
    FileType.YAML: PAIR_VALUE_KEYWORD_REGEX_TO_GROUP,
}

REGEX_VALUE_SECRET_BY_FILETYPE = {
    FileType.YAML: PAIR_VALUE_SECRET_REGEX_TO_GROUP,
}


class EntropyKeywordCombinator(BasePlugin):
    secret_type = ""  # nosec  # noqa: CCE003  # a static attribute

    def __init__(self, limit: float = ENTROPY_KEYWORD_LIMIT) -> None:
        iac_limit = ENTROPY_KEYWORD_COMBINATOR_LIMIT
        self.high_entropy_scanners_iac = (Base64HighEntropyString(limit=iac_limit), HexHighEntropyString(limit=iac_limit))
        self.high_entropy_scanners = (Base64HighEntropyString(limit=limit), HexHighEntropyString(limit=limit))
        self.keyword_scanner = KeywordDetector()

    def analyze_string(self, string: str) -> Generator[str, None, None]:
        pass

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
        value_keyword_regex_to_group = REGEX_VALUE_KEYWORD_BY_FILETYPE.get(filetype, None)
        secret_keyword_regex_to_group = REGEX_VALUE_SECRET_BY_FILETYPE.get(filetype, None)

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
                elif filetype == FileType.YAML:
                    return self.analyze_iac_line_yml(
                        filename=filename,
                        line=line,
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

    def analyze_iac_line_yml(
            self,
            filename: str,
            line: str,
            line_number: int = 0,
            context: CodeSnippet | None = None,
            raw_context: CodeSnippet | None = None,
            value_pattern: dict[Pattern[str], int] | None = None,
            secret_pattern: dict[Pattern[str], int] | None = None,
            **kwargs: Any,
    ) -> set[PotentialSecret]:
        secrets = set()
        if context is not None and raw_context is not None:
            value_secret = self.extract_from_string(pattern=secret_pattern, string=context.target_line)
            secret_adjust = self.format_reducing_noise_secret(value_secret)
            entropy_on_value = self.detect_secret(
                scanners=self.high_entropy_scanners,
                filename=filename,
                line=secret_adjust,
                line_number=line_number,
                kwargs=kwargs
            )

            if entropy_on_value:
                possible_keywords: set[str] = set()
                forward_range = range(context.target_index - 1, -1, -1)
                backwards_range = range(context.target_index + 1, len(context.lines))
                possible_keywords |= self.get_lines_from_same_object(forward_range, context, raw_context)
                possible_keywords |= self.get_lines_from_same_object(backwards_range, context, raw_context)

                for other_value in possible_keywords:
                    if self.extract_from_string(pattern=value_pattern, string=other_value):
                        secrets |= entropy_on_value
                        break
        return secrets

    def get_lines_from_same_object(
            self,
            search_range: range,
            context: CodeSnippet | None,
            raw_context: CodeSnippet | None
    ) -> set[str]:
        possible_keywords: set[str] = set()
        if not context or not raw_context:
            return possible_keywords
        for j in search_range:
            line = context.lines[j]
            if self.lines_in_same_object(raw_context=raw_context, idx=j) \
                    and not self.line_is_comment(line):
                possible_keywords.add(raw_context.lines[j])
                if self.is_object_start(raw_context=raw_context, idx=j):
                    return possible_keywords
        return possible_keywords

    @staticmethod
    def format_reducing_noise_secret(string: str) -> str:
        return json.dumps(string)

    def lines_in_same_object(
            self,
            raw_context: CodeSnippet | None,
            idx: int
    ) -> bool:
        if not raw_context:
            return False  # could not know
        return 0 <= idx < len(raw_context.lines) and 0 <= idx + 1 < len(raw_context.lines)\
            and self.lines_same_indentation(raw_context.lines[idx], raw_context.lines[idx + 1])

    @staticmethod
    def is_object_start(
            raw_context: CodeSnippet | None,
            idx: int
    ) -> bool:
        if not raw_context:
            return False  # could not know
        match = re.match(INDENTATION_PATTERN, raw_context.lines[idx])
        if match:
            return '-' in match.groups()[0]
        return False

    @staticmethod
    def line_is_comment(line: str) -> bool:
        if re.match(COMMENT_PREFIX, line):
            return True
        return False

    @staticmethod
    def extract_from_string(pattern: dict[Pattern[str], int] | None, string: str) -> str:
        if not pattern:
            return ''
        for value_regex, group_number in pattern.items():
            match = value_regex.search(string)
            if match:
                return match.group(group_number)
        return ''

    @staticmethod
    def lines_same_indentation(line1: str, line2: str) -> bool:
        match1 = re.match(INDENTATION_PATTERN, line1)
        match2 = re.match(INDENTATION_PATTERN, line2)
        if not match1 and not match2:
            return True
        if not match1 or not match2:
            return False
        indent1 = len(match1.groups()[0])
        indent2 = len(match2.groups()[0])
        if indent1 == indent2:
            return True
        return False

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
