from abc import ABCMeta

from detect_secrets.plugins.base import BasePlugin


class EntropyKeywordCombinator(BasePlugin, metaclass=ABCMeta):
    secret_type = 'Scans for High entropy strings and secret-sounding variable names'
