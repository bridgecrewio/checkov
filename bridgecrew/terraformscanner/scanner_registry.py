import logging


class ScannerRegistry():
    scanners = {}

    def __init__(self):
        self.logger = logging.getLogger("bridgecrew.scanner_registry")

    def register(self, scanner):
        resource = scanner.supported_resource
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
            self.logger.debug("Running scan: %s", scanner.name)
            scanner.scan(resource_configuration=resource_conf_def, resource_name=resource_name)
            result = scanner.scan_resource_conf(resource_conf_def)
            results.append(result)
        return results
