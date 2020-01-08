import logging

from checkov.terraform.models.enums import CheckResult


class Registry:
    checks = {}

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def register(self, check):
        for data in check.supported_data:
            if data not in self.checks.keys():
                self.checks[data] = []
            self.checks[data].append(check)

    def get_checks(self, data):
        if data in self.checks.keys():
            return self.checks[data]
        return []

    def scan(self, block, scanned_file, skipped_checks):
        data = list(block.keys())[0]
        data_conf = block[data]
        results = {}
        checks = self.get_checks(data)
        for check in checks:
            skip_info = {}
            if skipped_checks:
                if check.id in [x['id'] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x['id'] == check.id][0]
            data_name = list(data_conf.keys())[0]
            data_conf_def = data_conf[data_name]
            self.logger.debug("Running check: {} on file {}".format(check.name, scanned_file))
            result = check.run(scanned_file=scanned_file, entity_configuration=data_conf_def,
                               entity_name=data_name, entity_type=data, skip_info=skip_info)
            if check.__class__.__name__ == 'IAMParliament':
                if isinstance(result['result'], tuple):
                    for finding in result['result'][1]:
                        results[finding] = {'result': CheckResult.FAILED}
            else:
                results[check] = result
        return results


data_registry = Registry()
