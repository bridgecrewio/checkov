from __future__ import annotations

import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet

from checkov.secrets.parsers.multiline_parser import BaseMultiLineParser


START_OBJ_END_OF_LINE = r'({\s*}?\s*,?\s*$)'
START_OBJ_START_OF_LINE = r'(^\s*{)'

START_OBJ = re.compile(fr'{START_OBJ_START_OF_LINE}|{START_OBJ_END_OF_LINE}')
START_OBJ_INCLUDING_CURRENT_LINE = re.compile(START_OBJ_START_OF_LINE)
END_OBJ = re.compile(r'(^\s*\}\s*)|({?\s*\}\s*,?\s*$)')
WHOLE_OBJ_INLINE = re.compile(r'{[^{]*{?\s*\}\s*,?\s*$')


class JsonMultiLineParser(BaseMultiLineParser):

    def consecutive_lines_in_same_object(
        self,
        raw_context: CodeSnippet | None,
        other_line_idx: int,
    ) -> bool:
        if not raw_context or not 0 <= other_line_idx < len(raw_context.lines):
            return False
        higher_line = raw_context.lines[other_line_idx]
        lower_line = raw_context.target_line
        if other_line_idx > raw_context.target_index:
            higher_line, lower_line = lower_line, higher_line
        if self.is_object_end(higher_line) or re.search(START_OBJ_INCLUDING_CURRENT_LINE, lower_line):
            return False
        if self.is_object_start(higher_line):
            return bool(re.search(START_OBJ_INCLUDING_CURRENT_LINE, higher_line))
        return True

    @staticmethod
    def is_object_start(
        line: str
    ) -> bool:
        return bool(re.search(START_OBJ, line) and not re.search(WHOLE_OBJ_INLINE, line))

    @staticmethod
    def is_object_end(
        line: str
    ) -> bool:
        return bool(re.search(END_OBJ, line) and not re.search(WHOLE_OBJ_INLINE, line))

    @staticmethod
    def is_line_comment(
        line: str
    ) -> bool:
        return False


json_multiline_parser = JsonMultiLineParser()
