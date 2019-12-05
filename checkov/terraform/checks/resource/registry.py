import logging


class Registry():
    scanners = {}

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def register(self, scanner):
        for resource in scanner.supported_resources:
            if resource not in self.scanners.keys():
                self.scanners[resource] = []
            self.scanners[resource].append(scanner)

    def get_scanners(self, resource):
        if resource in self.scanners.keys():
            return self.scanners[resource]
        return []

    def scan(self, block, scanned_file):
        resource = list(block.keys())[0]
        resource_conf = block[resource]
        results = []
        for scanner in self.get_scanners(resource):
            resource_name = list(resource_conf.keys())[0]
            resource_conf_def = resource_conf[resource_name]
            self.logger.debug("Running scan: {} on file {}".format(scanner.name, scanned_file))
            result = scanner.scan(scanned_file=scanned_file, resource_configuration=resource_conf_def,
                                  resource_name=resource_name, resource_type=resource)
            results.append(result)
        return results


resource_registry = Registry()
