from __future__ import annotations

import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet

from checkov.common.parsers.multiline_parser import BaseMultiLineParser


START_OBJ_END_OF_LINE = r'({\s*}?\s*,?\s*$)'
START_OBJ_START_OF_LINE = r'(^\s*{)'

START_OBJ = re.compile(fr'{START_OBJ_START_OF_LINE}|{START_OBJ_END_OF_LINE}')
START_OBJ_INCLUDING_CURRENT_LINE = re.compile(START_OBJ_START_OF_LINE)
END_OBJ = re.compile(r'(^\s*\}\s*)|({?\s*\}\s*,?\s*$)')
WHOLE_OBJ_INLINE = re.compile(r'{[^{]*{?\s*\}\s*,?\s*$')


class JsonMultiLineParser(BaseMultiLineParser):

    def __init__(self) -> None:
        pass

    def consecutive_lines_in_same_object(
        self,
        raw_context: CodeSnippet | None,
        other_line_idx: int,
    ) -> bool:
        if not raw_context:
            return False  # could not know
        if not 0 <= other_line_idx < len(raw_context.lines):
            return False
        line1 = raw_context.lines[other_line_idx]
        line2 = raw_context.target_line
        if other_line_idx > raw_context.target_index:
            line1, line2 = line2, line1
        if not self.is_object_end(line1) and not re.search(START_OBJ_INCLUDING_CURRENT_LINE, line2):
            if self.is_object_start(line1):
                if re.search(START_OBJ_INCLUDING_CURRENT_LINE, line1):
                    return True
                return False
            return True
        return False

    @staticmethod
    def is_object_start(
        line: str
    ) -> bool:
        if re.search(START_OBJ, line) and not re.search(WHOLE_OBJ_INLINE, line):
            return True
        return False

    @staticmethod
    def is_object_end(
        line: str
    ) -> bool:
        if re.search(END_OBJ, line) and not re.search(WHOLE_OBJ_INLINE, line):
            return True
        return False

    @staticmethod
    def is_line_comment(
        line: str
    ) -> bool:
        return False


json_multiline_parser = JsonMultiLineParser()
