import logging
from abc import ABC, abstractmethod
from bridgecrew.terraformscanner.context_parsers.parser_registry import parser_registry
from bridgecrew.terraformscanner.models.enums import ContextCategories


class ContextParser(ABC):
    type = ""

    def __init__(self, type):
        self.logger = logging.getLogger("{}".format(self.__module__))
        if type not in ContextCategories.__members__:
            self.logger.error("Terraform context parser type not supported")
            raise Exception()

        self.type = type
        parser_registry.register(self)


    @abstractmethod
    def parse_definition_block(self, block):
        raise NotImplementedError()
