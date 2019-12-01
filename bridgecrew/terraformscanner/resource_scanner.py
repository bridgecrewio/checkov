import logging
from abc import ABC, abstractmethod

from bridgecrew.terraformscanner.models.enums import ScanResult
from bridgecrew.terraformscanner.scanner_registry import scanner_registry

class ResourceScanner(ABC):
    scan_id = ""
    name = ""
    categories = []

    def __init__(self, name, scan_id, categories, supported_resources):
        self.name = name
        self.scan_id = scan_id
        self.categories = categories
        self.supported_resources = supported_resources
        self.logger = logging.getLogger("{}".format(self.__module__))
        scanner_registry.register(self)

    def scan(self, scanned_file, resource_configuration, resource_name,resource_type):
        result = self.scan_resource_conf(resource_configuration)
        message = "File {}, Resource \"{}.{}\" Scan \"{}\" Result: {} ".format(scanned_file, resource_type, resource_name,
                                                                               self.name,
                                                                               result)
        if result == ScanResult.FAILURE:
            self.logger.warning(message)
        else:
            self.logger.info(message)

    @abstractmethod
    def scan_resource_conf(self, conf):
        raise NotImplementedError()
