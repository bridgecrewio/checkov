from checkov.common.bridgecrew.severities import Severities, get_severity
from checkov.common.checks.base_check_registry import BaseCheckRegistry


class Registry(BaseCheckRegistry):

    def extract_entity_details(self, entity):
        kind = entity["kind"]
        conf = entity
        return kind, conf

    def scan(self, scanned_file, entity, skipped_checks, runner_filter):
        (entity_type, entity_configuration) = self.extract_entity_details(entity)
        results = {}
        checks = self.get_checks(entity_type)
        for check in checks:
            skip_info = {}
            if skipped_checks:
                if check.id in [x['id'] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x['id'] == check.id][0]

            if self._should_run_scan(check, entity_configuration, runner_filter):
                self.logger.debug("Running check: {} on file {}".format(check.name, scanned_file))

                result = check.run(scanned_file=scanned_file, entity_configuration=entity_configuration,
                                   entity_name=entity_type, entity_type=entity_type, skip_info=skip_info)
                results[check] = result
        return results

    @staticmethod
    def _should_run_scan(check, entity_configuration, runner_filter):
        check_id_allowlist = runner_filter.checks
        check_id_denylist = runner_filter.skip_checks
        if check_id_allowlist or runner_filter.check_threshold:
            # Allow list provides namespace-only allows, check-only allows, or both
            # If namespaces not specified, all namespaces are scanned
            # If checks not specified, all checks are scanned
            run_check = False
            allowed_namespaces = [string for string in check_id_allowlist if ("CKV_" not in string and "BC_" not in string)]
            if not any(("CKV_" in check or "BC_" in check) for check in check_id_allowlist) and not runner_filter.check_threshold:
                if "metadata" in entity_configuration and "namespace" in entity_configuration["metadata"]:
                    if entity_configuration["metadata"]["namespace"] in allowed_namespaces:
                        run_check = True
                elif "parent_metadata" in entity_configuration and "namespace" in entity_configuration["parent_metadata"]:
                    if entity_configuration["parent_metadata"]["namespace"] in allowed_namespaces:
                        run_check = True
                else:
                    if "default" in allowed_namespaces:
                        run_check = True
            else:
                if runner_filter.should_run_check(check=check):
                    if allowed_namespaces:
                        # Check if namespace in allowed namespaces
                        if "metadata" in entity_configuration and "namespace" in entity_configuration["metadata"]:
                            if entity_configuration["metadata"]["namespace"] in allowed_namespaces:
                                run_check = True
                        elif "parent_metadata" in entity_configuration and "namespace" in entity_configuration["parent_metadata"]:
                            if entity_configuration["parent_metadata"]["namespace"] in allowed_namespaces:
                                run_check = True
                        else:
                            if "default" in allowed_namespaces:
                                run_check = True
                    else:
                        # No namespaces to filter
                        run_check = True
            if run_check:
                return True
        elif check_id_denylist or runner_filter.skip_check_threshold:
            namespace_skip = False
            if "metadata" in entity_configuration and "namespace" in entity_configuration["metadata"]:
                if entity_configuration["metadata"]["namespace"] in check_id_denylist:
                    namespace_skip = True
            elif "parent_metadata" in entity_configuration and "namespace" in entity_configuration["parent_metadata"]:
                if entity_configuration["parent_metadata"]["namespace"] in check_id_denylist:
                    namespace_skip = True
            else:
                if "default" in check_id_denylist:
                    namespace_skip = True
            if runner_filter.should_run_check(check=check) and not namespace_skip:
                return True
        else:
            return True
        return False
