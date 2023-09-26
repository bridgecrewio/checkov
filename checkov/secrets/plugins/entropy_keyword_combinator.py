from __future__ import annotations

import re
from typing import Generator, Set, Tuple
from typing import Any
from typing import TYPE_CHECKING

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

from detect_secrets.util.filetype import determine_file_type
from checkov.secrets.plugins.detector_utils import SINGLE_LINE_PARSER, MULTILINE_PARSERS, \
    REGEX_VALUE_KEYWORD_BY_FILETYPE, REGEX_VALUE_SECRET_BY_FILETYPE, remove_fp_secrets_in_keys, detect_secret, \
    analyze_multiline_keyword_combinator, mark_set_multiline

from checkov.secrets.runner import SOURCE_CODE_EXTENSION

if TYPE_CHECKING:
    from detect_secrets.core.potential_secret import PotentialSecret
    from detect_secrets.util.code_snippet import CodeSnippet

MAX_LINE_LENGTH = 10000
MAX_KEYWORD_LIMIT = 500
ENTROPY_KEYWORD_COMBINATOR_LIMIT = 3
ENTROPY_KEYWORD_LIMIT = 4.8

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


class EntropyKeywordCombinator(BasePlugin):
    secret_type = ""  # nosec  # noqa: CCE003  # a static attribute

    def __init__(self, limit: float = ENTROPY_KEYWORD_LIMIT, max_line_length: int = MAX_LINE_LENGTH) -> None:
        iac_limit = ENTROPY_KEYWORD_COMBINATOR_LIMIT
        self.high_entropy_scanners_iac = (Base64HighEntropyString(limit=iac_limit), HexHighEntropyString(limit=iac_limit))
        self.entropy_scanners_non_iac_with_keyword = (Base64HighEntropyString(limit=iac_limit + 0.3), HexHighEntropyString(limit=iac_limit + 0.3))
        self.high_entropy_scanners = (Base64HighEntropyString(limit=limit), HexHighEntropyString(limit=limit))
        self.keyword_scanner = KeywordDetector()
        self.max_line_length = max_line_length

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
        if len(line) > self.max_line_length:
            # to keep good performance we skip long lines
            return set()

        is_iac = f".{filename.split('.')[-1]}" not in SOURCE_CODE_EXTENSION
        keyword_on_key = self.keyword_scanner.analyze_line(filename, line, line_number, **kwargs)
        if is_iac:
            filetype = determine_file_type(filename)
            single_line_parser = SINGLE_LINE_PARSER.get(filetype)
            multiline_parsers = MULTILINE_PARSERS.get(filetype)

            # classic key-value pair
            if keyword_on_key:
                if single_line_parser:
                    # Getting last detected one as only 1 violation available for line
                    secret_value, quoted_secret = EntropyKeywordCombinator.receive_last_secret_detected(keyword_on_key)
                    old_line = line
                    line = quoted_secret if quoted_secret else line
                    detected_secrets = single_line_parser.detect_secret(
                        scanners=self.high_entropy_scanners_iac,
                        filename=filename,
                        raw_context=raw_context,
                        line=line,
                        line_number=line_number,
                        kwargs=kwargs
                    )
                    remove_fp_secrets_in_keys(detected_secrets, old_line)
                    return detected_secrets
                else:
                    # preprocess line before detecting secrets - add quotes on potential secrets to allow triggering
                    # entropy detector
                    secret_value, quoted_secret = EntropyKeywordCombinator.receive_last_secret_detected(keyword_on_key)
                    if line.find(quoted_secret) < 0:    # replace potential secret with quoted version
                        line = line.replace(secret_value, quoted_secret, 1)
                    detected_secrets = detect_secret(
                        scanners=self.high_entropy_scanners_iac,
                        filename=filename,
                        line=line,
                        line_number=line_number,
                        kwargs=kwargs
                    )
                    # postprocess detected secrets - filter out potential secrets on keyword
                    remove_fp_secrets_in_keys(detected_secrets, line)
                    return detected_secrets

            # not so classic key-value pair, from multiline, that is only in an array format.
            # The scan searches forwards and backwards for a potential secret pair, so no duplicates expected.
            elif multiline_parsers:
                # iterate over multiple parser and their related file type.
                # this is needed for file types, which embed other file type parser, ex Terraform with heredoc
                for parser_file_type, multiline_parser in multiline_parsers:
                    value_keyword_regex_to_group = REGEX_VALUE_KEYWORD_BY_FILETYPE.get(parser_file_type)
                    secret_keyword_regex_to_group = REGEX_VALUE_SECRET_BY_FILETYPE.get(parser_file_type)

                    potential_secrets = analyze_multiline_keyword_combinator(
                        filename=filename,
                        scanners=self.high_entropy_scanners,
                        multiline_parser=multiline_parser,
                        line_number=line_number,
                        context=context,
                        raw_context=raw_context,
                        value_pattern=value_keyword_regex_to_group,
                        secret_pattern=secret_keyword_regex_to_group,
                        kwargs=kwargs
                    )

                    if potential_secrets:
                        mark_set_multiline(potential_secrets)
                        # return a possible secret, otherwise check with next parser
                        return potential_secrets
        else:
            detected_secrets = detect_secret(
                # If we found a keyword (i.e. db_pass = ), lower the threshold to the iac threshold
                scanners=self.high_entropy_scanners if not keyword_on_key else self.entropy_scanners_non_iac_with_keyword,
                filename=filename,
                line=line,
                line_number=line_number,
                kwargs=kwargs
            )
            if detected_secrets:
                remove_fp_secrets_in_keys(detected_secrets, line, True)
            return detected_secrets

        return set()

    @staticmethod
    def convert_to_reduce_noise(secret_value: str) -> str:
        # For empty string return empty string
        if not secret_value:
            return ''
        return f"\"{secret_value}\""

    @staticmethod
    def receive_last_secret_detected(keyword_on_key: Set[PotentialSecret]) -> Tuple[str, str]:
        return_value = ''
        quoted_return_value = ''
        for pt in keyword_on_key:
            if pt.secret_value:
                return_value = pt.secret_value
                quoted_return_value = EntropyKeywordCombinator.convert_to_reduce_noise(pt.secret_value)
        return return_value, quoted_return_value
