from detect_secrets.plugins.high_entropy_strings import Base64HighEntropyString, HexHighEntropyString
from detect_secrets.plugins.keyword import KeywordDetector
from detect_secrets.plugins.base import BasePlugin
from typing import Generator


class EntropyKeywordCombinator(BasePlugin):
    secret_type = 'Scans for High entropy strings and secret-sounding variable names'

    def __init__(self, limit: float) -> None:
        self.high_entropy_scanner = (Base64HighEntropyString(limit=limit), HexHighEntropyString(limit=limit))
        self.keyword_scanner = KeywordDetector()
        print(1)
        # TODO

    def analyze_string(self, string: str) -> Generator[str, None, None]:
        return iter(["1"])
