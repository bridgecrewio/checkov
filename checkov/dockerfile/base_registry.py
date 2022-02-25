from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.models.enums import CheckResult
from checkov.common.typing import _SkippedCheck


class Registry(BaseCheckRegistry):
    def scan(self, scanned_file, entity, skipped_checks, runner_filter):

        results = {}
        if not entity:
            return results
        for instruction, checks in self.checks.items():
            if instruction in entity:
                for check in checks:
                    skip_info: _SkippedCheck = {}
                    if skipped_checks:
                        # if there is a severity skip, it will be at the end
                        if check.id in [x["id"] for x in skipped_checks if "id" in x]:
                            skip_info = [x for x in skipped_checks if x.get("id") == check.id][0]
                        elif check.bc_severity and "severity" in skipped_checks[-1] and check.bc_severity.level <= \
                                skipped_checks[-1]["severity"].level:
                            skip_info = skipped_checks[-1]

                    if runner_filter.should_run_check(check):
                        entity_name = instruction
                        entity_type = instruction
                        entity_configuration = entity[instruction]
                        self.update_result(check, entity_configuration, entity_name, entity_type, results, scanned_file,
                                           skip_info)

        for check in self.wildcard_checks["*"]:
            skip_info: _SkippedCheck = {}
            if skipped_checks:
                # if there is a severity skip, it will be at the end
                if check.id in [x["id"] for x in skipped_checks if "id" in x]:
                    skip_info = [x for x in skipped_checks if x.get("id") == check.id][0]
                elif check.bc_severity and "severity" in skipped_checks[-1] and check.bc_severity.level <= \
                        skipped_checks[-1]["severity"].level:
                    skip_info = skipped_checks[-1]

            if runner_filter.should_run_check(check):
                entity_name = scanned_file
                entity_type = "*"
                entity_configuration = entity
                self.update_result(check, entity_configuration, entity_name, entity_type, results, scanned_file,
                                   skip_info)
        return results

    def update_result(self, check, entity_configuration, entity_name, entity_type, results, scanned_file, skip_info):
        result = self.run_check(check, entity_configuration, entity_name, entity_type, scanned_file,
                                skip_info)
        results[check] = {}
        if result['result'] == CheckResult.SKIPPED:
            results[check]['result'] = result['result']
            results[check]['suppress_comment'] = result['suppress_comment']
            results[check]['results_configuration'] = None
        else:
            results[check]['result'] = result['result'][0]
            results[check]['results_configuration'] = result['result'][1]
