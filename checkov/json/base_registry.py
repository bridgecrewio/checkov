from checkov.common.checks.base_check_registry import BaseCheckRegistry
from checkov.common.models.enums import CheckResult
from checkov.json.enums import BlockType


class Registry(BaseCheckRegistry):
    def __init__(self):
        super().__init__()
        self._scanner = {
            BlockType.ARRAY: self._scan_json_array,
            BlockType.OBJECT: self._scan_json_object,
        }

    def _scan_json_array(
        self, scanned_file, check, skip_info, entity, entity_name, entity_type, results
    ):
        for item in entity:
            if entity_name in item:
                result = self.update_result(
                    check,
                    item[entity_name],
                    entity_name,
                    entity_type,
                    results,
                    scanned_file,
                    skip_info,
                )

                if result == CheckResult.FAILED:
                    break

    def _scan_json_object(
        self, scanned_file, check, skip_info, entity, entity_name, entity_type, results
    ):
        if entity_name in entity:
            self.update_result(
                check,
                entity[entity_name],
                entity_name,
                entity_type,
                results,
                scanned_file,
                skip_info,
            )

    def _scan_json_document(
        self, scanned_file, check, skip_info, entity, entity_name, entity_type, results
    ):
        self.update_result(
            check, entity, entity_name, entity_type, results, scanned_file, skip_info
        )

    def _scan_json(
        self,
        scanned_file,
        checks,
        skipped_checks,
        runner_filter,
        entity,
        entity_name,
        entity_type,
        results,
    ):
        for check in checks:
            skip_info = ([x for x in skipped_checks if x["id"] == check.id] or [{}])[0]

            if runner_filter.should_run_check(check.id, check.bc_id):
                scanner = self._scanner.get(check.block_type, self._scan_json_document)
                if check.path:
                    target = entity
                    for p in check.path.split("."):
                        if p.endswith("]"):
                            ip = p.split("[")
                            i = int(ip[1][:-1])
                            target = target[ip[0]][i]
                        else:
                            target = target[p]
                else:
                    target = entity
                scanner(
                    scanned_file,
                    check,
                    skip_info,
                    target,
                    entity_name,
                    entity_type,
                    results,
                )

    def scan(self, scanned_file, entity, skipped_checks, runner_filter):
        results = {}

        if not entity:
            return results

        for instruction, checks in self.checks.items():
            self._scan_json(
                scanned_file=scanned_file,
                checks=checks,
                skipped_checks=skipped_checks,
                runner_filter=runner_filter,
                entity=entity,
                entity_name=instruction,
                entity_type=instruction,
                results=results,
            )

        if self.wildcard_checks["*"]:
            self._scan_json(
                scanned_file=scanned_file,
                checks=self.wildcard_checks["*"],
                skipped_checks=skipped_checks,
                runner_filter=runner_filter,
                entity=entity,
                entity_name=scanned_file,
                entity_type="*",
                results=results,
            )

        return results

    def update_result(
        self,
        check,
        entity_configuration,
        entity_name,
        entity_type,
        results,
        scanned_file,
        skip_info,
    ):
        result = self.run_check(
            check,
            entity_configuration,
            entity_name,
            entity_type,
            scanned_file,
            skip_info,
        )

        results[check] = {}
        if result["result"] == CheckResult.SKIPPED:
            results[check]["result"] = result["result"]
            results[check]["suppress_comment"] = result["suppress_comment"]
            results[check]["results_configuration"] = None
        else:
            results[check]["result"] = result["result"][0]
            results[check]["results_configuration"] = result["result"][1]

        return result["result"][0]
