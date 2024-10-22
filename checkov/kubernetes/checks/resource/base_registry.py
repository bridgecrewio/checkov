from __future__ import annotations

from typing import Any, TYPE_CHECKING

from checkov.common.checks.base_check_registry import BaseCheckRegistry

if TYPE_CHECKING:
    from checkov.common.checks.base_check import BaseCheck
    from checkov.common.typing import _SkippedCheck, _CheckResult
    from checkov.runner_filter import RunnerFilter


class Registry(BaseCheckRegistry):
    def __init__(self, report_type: str) -> None:
        super().__init__(report_type)

    def extract_entity_details(self, entity: dict[str, Any]) -> tuple[str, dict[str, Any]]:  # type:ignore[override]
        kind = entity.get("kind") or ""
        conf = entity
        return kind, conf

    def scan(
        self,
        scanned_file: str,
        entity: dict[str, Any],
        skipped_checks: list[_SkippedCheck],
        runner_filter: RunnerFilter,
        report_type: str | None = None,
    ) -> dict[BaseCheck, _CheckResult]:
        (entity_type, entity_configuration) = self.extract_entity_details(entity)
        results = {}
        checks = self.get_checks(entity_type)
        for check in checks:
            skip_info: "_SkippedCheck" = {}
            if skipped_checks:
                if check.id in [x['id'] for x in skipped_checks]:
                    skip_info = [x for x in skipped_checks if x['id'] == check.id][0]

            if self._should_run_scan(check, entity_configuration, runner_filter, self.report_type):
                self.logger.debug("Running check: {} on file {}".format(check.name, scanned_file))

                result = check.run(scanned_file=scanned_file, entity_configuration=entity_configuration,
                                   entity_name=entity_type, entity_type=entity_type, skip_info=skip_info)
                results[check] = result
        return results

    @staticmethod
    def _should_run_scan(
        check: BaseCheck, entity_configuration: dict[str, Any], runner_filter: RunnerFilter, report_type: str
    ) -> bool:
        check_id_allowlist = runner_filter.checks
        check_id_denylist = runner_filter.skip_checks
        if check_id_allowlist or runner_filter.check_threshold:
            # Allow list provides namespace-only allows, check-only allows, or both
            # If namespaces not specified, all namespaces are scanned
            # If checks not specified, all checks are scanned

            if any("_" in check_id for check_id in check_id_allowlist) or runner_filter.check_threshold:
                # a Kubernetes namespace can't have an '_' in its name,
                # therefore we assume it is a built-in or custom check
                if not runner_filter.should_run_check(check=check, report_type=report_type):
                    return False

            allowed_namespaces = [check_id for check_id in check_id_allowlist if "_" not in check_id]
            if allowed_namespaces:
                # Check if namespace in allowed namespaces
                if "metadata" in entity_configuration and "namespace" in entity_configuration["metadata"]:
                    if entity_configuration["metadata"]["namespace"] in allowed_namespaces:
                        return True
                elif "parent_metadata" in entity_configuration and "namespace" in entity_configuration["parent_metadata"]:
                    if entity_configuration["parent_metadata"]["namespace"] in allowed_namespaces:
                        return True
                else:
                    if "default" in allowed_namespaces:
                        return True
            else:
                # No namespaces to filter
                return True
        elif check_id_denylist or runner_filter.skip_check_threshold or runner_filter.use_enforcement_rules:
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
            if runner_filter.should_run_check(check=check, report_type=report_type) and not namespace_skip:
                return True
        else:
            return True
        return False
