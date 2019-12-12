import logging
from abc import ABC, abstractmethod

from checkov.terraform.checks.resource.registry import resource_registry
from checkov.terraform.models.enums import CheckResult

class BaseResourceCheck(ABC):
    id = ""
    name = ""
    categories = []

    def __init__(self, name, id, categories, supported_resources):
        self.name = name
        self.id = id
        self.categories = categories
        self.supported_resources = supported_resources
        self.logger = logging.getLogger("{}".format(self.__module__))
        resource_registry.register(self)

    def run(self, scanned_file, resource_configuration, resource_name, resource_type, skip=False):
        if skip:
            result = CheckResult.SKIPPED
        else:
            result = self.scan_resource_conf(resource_configuration)
        message = "File {}, Resource \"{}.{}\" check \"{}\" Result: {} ".format(scanned_file, resource_type,
                                                                                resource_name,
                                                                                self.name,
                                                                                result)
        self.logger.debug(message)
        return result

    @abstractmethod
    def scan_resource_conf(self, conf):
        raise NotImplementedError()
