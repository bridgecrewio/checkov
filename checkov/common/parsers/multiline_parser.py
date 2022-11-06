from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC
from abc import abstractmethod

if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet


class BaseMultiLineParser(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_lines_from_same_object(
        self,
        search_range: range,
        context: CodeSnippet | None,
        raw_context: CodeSnippet | None
    ) -> set[str]:
        pass
