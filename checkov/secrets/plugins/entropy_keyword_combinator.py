from detect_secrets.core.potential_secret import PotentialSecret
from detect_secrets.plugins.high_entropy_strings import Base64HighEntropyString, HexHighEntropyString
from detect_secrets.plugins.keyword import KeywordDetector
from detect_secrets.plugins.base import BasePlugin
from typing import Generator, Any, Set


class EntropyKeywordCombinator(BasePlugin):
    secret_type = None

    def __init__(self, limit: float) -> None:
        self.high_entropy_scanners = (Base64HighEntropyString(limit=limit), HexHighEntropyString(limit=limit))
        self.keyword_scanner = KeywordDetector()

    def analyze_line(
            self,
            filename: str,
            line: str,
            line_number: int = 0,
            **kwargs: Any
    ) -> Set[PotentialSecret]:
        """
        This method first runs the keyword plugin. If it finds a match - it runs the entropy scanners, and if
        one of the entropy scanners find a match (on a line which was already matched by keyword plugin) - it is returned.
        """
        keyword_matches = self.keyword_scanner.analyze_line(filename, line, line_number, **kwargs)
        if keyword_matches:
            for entropy_scanner in self.high_entropy_scanners:
                matches = entropy_scanner.analyze_line(filename, line, line_number, **kwargs)
                if matches:
                    return matches
        return set([])

    def analyze_string(self, string: str) -> Generator[str, None, None]:
        raise NotImplementedError()
