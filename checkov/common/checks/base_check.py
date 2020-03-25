import logging
from abc import ABC, abstractmethod

from checkov.common.models.enums import CheckResult


class BaseCheck(ABC):
    id = ""
    name = ""
    categories = []
    supported_entities = []

    def __init__(self, name, id, categories, supported_entities, block_type):
        self.name = name
        self.id = id
        self.categories = categories
        self.block_type = block_type
        self.supported_entities = supported_entities
        self.logger = logging.getLogger("{}".format(self.__module__))

    def run(self, scanned_file, entity_configuration, entity_name, entity_type, skip_info):
        check_result = {}
        if skip_info:
            check_result['result'] = CheckResult.SKIPPED
            check_result['suppress_comment'] = skip_info['suppress_comment']
            message = "File {}, {} \"{}.{}\" check \"{}\" Result: {}, Suppression comment: {} ".format(
                scanned_file, self.block_type, entity_type,
                entity_name,
                self.name,
                check_result, check_result['suppress_comment'])
        else:
            try:
                check_result['result'] = self.scan_entity_conf(entity_configuration)
                message = "File {}, {}  \"{}.{}\" check \"{}\" Result: {} ".format(scanned_file, self.block_type,
                                                                                   entity_type,
                                                                                   entity_name,
                                                                                   self.name,
                                                                                   check_result)
                self.logger.debug(message)

            except Exception as e:
                self.logger.error(
                    "Failed to run check: {} for configuration: {} at file: {}".format(self.name, str(entity_configuration),scanned_file))
                raise e
        return check_result

    @abstractmethod
    def scan_entity_conf(self, conf):
        raise NotImplementedError()
