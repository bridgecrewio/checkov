import logging
from abc import ABC, abstractmethod

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

    def scan(self, scanned_file, resource_configuration, resource_name):
        result = self.scan_resource_conf(resource_configuration)
        self.logger.info("File {}, Resource \"{}.{}\" Scan \"{}\" Result: {} ".format(scanned_file, self.supported_resources, resource_name,
                                                                                      self.name,
                                                                                      result))

    @abstractmethod
    def scan_resource_conf(self, conf):
        raise NotImplementedError()
