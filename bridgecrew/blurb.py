import hcl2
import os
import logging
from abc import ABC, abstractmethod
from enum import Enum
import json

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.INFO)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# tell the handler to use this format
console.setFormatter(formatter)


class ScanResult(Enum):
    SUCCESS = 1
    FAILURE = 2
    UNKNOWN = 3


class ScanCategories(Enum):
    LOGGING = 1
    ENCRYPTION = 2
    GENERAL_SECURITY = 3
    NETWORKING = 4
    IAM = 5



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


scanner_registry = ScannerRegistry()


class Scanner(ABC):
    scan_id = ""
    name = ""
    categories = []

    def __init__(self, name, scan_id, categories, supported_resource):
        self.name = name
        self.scan_id = scan_id
        self.categories = categories
        self.supported_resource = supported_resource
        self.logger = logging.getLogger("bridgecrew.scanner.%s" % scan_id)
        scanner_registry.register(self)

    def scan(self, resource_configuration, resource_name):
        result = self.scan_resource_conf(resource_configuration)
        self.logger.info("Resource \"%s.%s\" Scan \"%s\" Result: %s ", self.supported_resource, resource_name,
                         self.name,
                         result)

    @abstractmethod
    def scan_resource_conf(self, conf):
        raise NotImplementedError()


class S3AccessLogsScanner(Scanner):
    def __init__(self):
        name = "Ensure the S3 bucket has access logging enabled"
        scan_id = "BC_AWS_S3_13"
        supported_resource = 'aws_s3_bucket'
        categories = [ScanCategories.LOGGING]
        super().__init__(name=name, scan_id=scan_id, categories=categories, supported_resource=supported_resource)

    def scan_resource_conf(self, conf):
        """
            Looks for logging configuration at aws_s3_bucket:
            https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
        :param conf: aws_s3_bucket configuration
        :return: <ScanResult>
        """
        if 'logging' in conf.keys():
            return ScanResult.SUCCESS
        else:
            return ScanResult.FAILURE


s3 = S3AccessLogsScanner()


class Parser():
    def hcl2(self, directory, tf_defenitions={}):
        modules_scan = []
        for file in os.listdir(directory):
            if file.endswith(".tf"):
                tf_file = os.path.join(directory, file)
                if tf_file not in tf_defenitions.keys():
                    with(open(tf_file, 'r')) as file:
                        dict = hcl2.load(file)
                        tf_defenition = dict
                        tf_defenitions[tf_file] = tf_defenition
                        for modules in dict.get("module", []):
                            for module in modules.values():
                                relative_path = module['source'][0]
                                abs_path = os.path.join(directory, relative_path)
                                modules_scan.append(abs_path)
        for m in modules_scan:
            self.hcl2(directory=m, tf_defenitions=tf_defenitions)


tf_defenitions = {}
param = "/Users/barak/Documents/dev/platform2/src/stacks/baseStack"
Parser().hcl2(directory=param, tf_defenitions=tf_defenitions)
for definition in tf_defenitions.items():
    scanned_file = definition[0].split(param)[1]
    logging.info("Scanning file: %s", scanned_file)
    if 'resource' in definition[1]:
        for resource in definition[1]['resource']:
            scanner_registry.scan(resource, scanned_file)
