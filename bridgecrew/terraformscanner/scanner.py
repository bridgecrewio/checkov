import logging
from abc import ABC, abstractmethod

from bridgecrew.terraformscanner.scanner_registry import scanner_registry

class Scanner(ABC):
    scan_id = ""
    name = ""
    categories = []

    def __init__(self, name, scan_id, categories, supported_resource):
        self.name = name
        self.scan_id = scan_id
        self.categories = categories
        self.supported_resource = supported_resource
        self.logger = logging.getLogger("{}.{}".format(__name__, scan_id))
        scanner_registry.register(self)

    def scan(self, resource_configuration, resource_name):
        result = self.scan_resource_conf(resource_configuration)
        self.logger.info("Resource \"{}.{}\" Scan \"{}\" Result: {} ".format(self.supported_resource, resource_name,
                                                                             self.name,
                                                                             result))

    @abstractmethod
    def scan_resource_conf(self, conf):
        raise NotImplementedError()
