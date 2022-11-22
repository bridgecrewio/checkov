from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet

from checkov.secrets.parsers.multiline_parser import BaseMultiLineParser

INDENTATION_PATTERN = re.compile(r'(^\s*(?:-?\s+)?)')
COMMENT_PREFIX = re.compile(r'^[\s]*(#|\/\/)')


class YmlMultilineParser(BaseMultiLineParser):

    def consecutive_lines_in_same_object(
        self,
        raw_context: CodeSnippet | None,
        other_line_idx: int,
    ) -> bool:
        if not raw_context:
            return False  # could not know
        return 0 <= other_line_idx < len(raw_context.lines) and \
            self.lines_same_indentation(raw_context.lines[other_line_idx], raw_context.target_line)

    @staticmethod
    def is_object_start(
        line: str,
    ) -> bool:
        match = re.match(INDENTATION_PATTERN, line)
        if match:
            return '-' in match.groups()[0]
        return False

    @staticmethod
    def is_object_end(
        line: str,
    ) -> bool:
        match = re.match(INDENTATION_PATTERN, line)
        if match:
            return '-' in match.groups()[0]
        return False

    @staticmethod
    def is_line_comment(
        line: str
    ) -> bool:
        return bool(re.match(COMMENT_PREFIX, line))

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
        return indent1 == indent2


yml_multiline_parser = YmlMultilineParser()
