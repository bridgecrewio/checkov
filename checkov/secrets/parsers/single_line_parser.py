from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING


if TYPE_CHECKING:
    from detect_secrets.core.potential_secret import PotentialSecret
    from detect_secrets.plugins.high_entropy_strings import Base64HighEntropyString, HexHighEntropyString
    from detect_secrets.util.code_snippet import CodeSnippet


class BaseSingleLineParser(ABC):
    def detect_secret(
        self,
        scanners: tuple[Base64HighEntropyString, HexHighEntropyString],
        filename: str,
        raw_context: CodeSnippet | None,
        line: str,
        line_number: int = 0,
        **kwargs: Any,
    ) -> set[PotentialSecret]:
        for entropy_scanner in scanners:
            matches = entropy_scanner.analyze_line(filename, line, line_number, **kwargs)
            if matches:
                if raw_context and self.ignore_secret(raw_context=raw_context):
                    return set()

                return matches
        return set()

    @abstractmethod
    def ignore_secret(self, raw_context: CodeSnippet) -> bool:
        """Check for false-positive secrets by leveraging the context"""

        pass
