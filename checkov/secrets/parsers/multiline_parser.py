from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC
from abc import abstractmethod

if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet


class BaseMultiLineParser(ABC):
    def get_lines_from_same_object(
        self,
        search_range: range,
        context: CodeSnippet | None,
        raw_context: CodeSnippet | None,
        line_length_limit: int = 0,
    ) -> set[str]:
        possible_keywords: set[str] = set()

        if not context or not raw_context:
            return possible_keywords
        for j in search_range:
            line = raw_context.lines[j]
            if line_length_limit and len(line) > line_length_limit:
                continue
            if self.consecutive_lines_in_same_object(raw_context=raw_context, other_line_idx=j) \
                    and not self.is_line_comment(line):
                possible_keywords.add(raw_context.lines[j])
                if self.is_object_start(line=line) or self.is_object_end(line=line):
                    return possible_keywords
        # No start of array detected, hence all found possible_keywords are irrelevant
        return set()

    @abstractmethod
    def consecutive_lines_in_same_object(
        self,
        raw_context: CodeSnippet | None,
        other_line_idx: int,
    ) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def is_object_start(
        line: str,
    ) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def is_object_end(
        line: str,
    ) -> bool:
        pass

    @staticmethod
    @abstractmethod
    def is_line_comment(
        line: str
    ) -> bool:
        pass
