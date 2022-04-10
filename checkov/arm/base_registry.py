from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):

    def extract_entity_details(self, entity):
        resource_name, resource = next(iter(entity.items()))
        resource_type = str(resource.get('type', ''))    # entity['type'] ??
        return resource_type, resource_name, resource


'''
    def scan(self, scanned_file, entity, skipped_checks, runner_filter=None):
        entity_type, entity_configuration = self.extract_entity_details(entity)
        results = {}
        checks = self.get_checks(entity_type)
        for check in checks:
            skip_info = {}
            if skipped_checks:
                if check.id in [x['id'] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x['id'] == check.id][0]
                    
            if runner_filter.should_run_check(check.id):
                self.logger.debug("Running check: {} on file {}".format(check.name, scanned_file))
                result = check.run(scanned_file=scanned_file, entity_configuration=entity_configuration,
                                   entity_name=entity_type, entity_type=entity_type, skip_info=skip_info)
                results[check] = result
        return results
'''