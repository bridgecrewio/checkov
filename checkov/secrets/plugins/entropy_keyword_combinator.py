from abc import ABCMeta

from detect_secrets.plugins.base import BasePlugin
from detect_secrets.plugins.high_entropy_strings import HighEntropyStringsPlugin
from detect_secrets.plugins.keyword import KeywordDetector


class EntropyKeywordCombinator(BasePlugin, HighEntropyStringsPlugin, KeywordDetector, metaclass=ABCMeta):
    secret_type = 'Scans for High entropy strings and secret-sounding variable names'
