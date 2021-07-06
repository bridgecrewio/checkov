from detect_secrets.plugins.high_entropy_strings import Base64HighEntropyString, HexHighEntropyString
from detect_secrets.plugins.keyword import KeywordDetector
from detect_secrets.plugins.base import    BasePlugin
from typing import Generator
from checkov.common.util.data_structures_utils import generator_reader_wrapper


class EntropyKeywordCombinator(BasePlugin):
    secret_type = None

    def __init__(self, limit: float) -> None:
        self.high_entropy_scanners = (Base64HighEntropyString(limit=limit), HexHighEntropyString(limit=limit))
        self.keyword_scanner = KeywordDetector()

    def analyze_string(self, string: str) -> Generator[str, None, None]:
        keyword_secrets_generator = self.keyword_scanner.analyze_string(string)
        potential_entropy_secrets = []
        potential_kw_secret = generator_reader_wrapper(keyword_secrets_generator)
        if not potential_kw_secret:
            return
        for entropy_scanner in self.high_entropy_scanners:
            potential_entropy_secret = generator_reader_wrapper(entropy_scanner.analyze_string(string))
            if potential_entropy_secret:
                self.secret_type = entropy_scanner.secret_type
                potential_entropy_secrets.append(potential_entropy_secret)
        if potential_kw_secret and len(potential_entropy_secrets) > 0:
            yield string


