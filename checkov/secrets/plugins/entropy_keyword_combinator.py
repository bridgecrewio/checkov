from abc import ABCMeta
from detect_secrets.plugins.high_entropy_strings import HighEntropyStringsPlugin
from detect_secrets.plugins.keyword import KeywordDetector


class EntropyKeywordCombinator(HighEntropyStringsPlugin, KeywordDetector, metaclass=ABCMeta):
    secret_type = 'Scans for High entropy strings and secret-sounding variable names'

    def __init__(self, charset: str, limit: float) -> None:
        pass
        # TODO
