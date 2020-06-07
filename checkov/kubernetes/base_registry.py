from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):

    def __init__(self):
        super().__init__()

    def extract_entity_details(self, entity):
        kind = entity["kind"]
        conf = entity
        return kind, conf

    def scan(self, scanned_file, entity, skipped_checks, runner_filter=None):
        (entity_type, entity_configuration) = self.extract_entity_details(entity)
        results = {}
        checks = self.get_checks(entity_type)
        check_id_allowlist = runner_filter.checks
        check_id_denylist = runner_filter.skip_checks
        for check in checks:
            skip_info = {}
            if skipped_checks:
                if check.id in [x['id'] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x['id'] == check.id][0]
            if check_id_allowlist:
                if check.id in check_id_allowlist:
                    self.logger.debug("Running check: {} on file {}".format(check.name, scanned_file))

                    result = check.run(scanned_file=scanned_file, entity_configuration=entity_configuration,
                                       entity_name=entity_type, entity_type=entity_type, skip_info=skip_info)
                    results[check] = result
            elif check_id_denylist:
                if check.id not in check_id_denylist:
                    result = check.run(scanned_file=scanned_file, entity_configuration=entity_configuration,
                                       entity_name=entity_type, entity_type=entity_type, skip_info=skip_info)
                    results[check] = result
            else:
                self.logger.debug("Running check: {} on file {}".format(check.name, scanned_file))
                result = check.run(scanned_file=scanned_file, entity_configuration=entity_configuration,
                                   entity_name=entity_type, entity_type=entity_type, skip_info=skip_info)

                results[check] = result
        return results
