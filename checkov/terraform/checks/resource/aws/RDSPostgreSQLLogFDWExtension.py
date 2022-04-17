from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.common.util.type_forcers import force_int
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RDSPostgreSQLLogFDWExtension(BaseResourceCheck):
    def __init__(self) -> None:
        # https://aws.amazon.com/security/security-bulletins/AWS-2022-004/
        name = "Ensure that RDS PostgreSQL instances use a non vulnerable version with the log_fdw extension (https://aws.amazon.com/security/security-bulletins/AWS-2022-004/)"
        id = "CKV_AWS_250"
        supported_resources = ("aws_rds_cluster", "aws_db_instance")
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        self.evaluated_keys = ["engine"]

        if conf.get("engine") == ["postgres"]:
            self.evaluated_keys.append("engine_version")

            engine_version = conf.get("engine_version")
            if engine_version and isinstance(engine_version, list) and isinstance(engine_version[0], str):
                version_parts = engine_version[0].split(".")
                if 1 < len(version_parts) <= 3:
                    major_version = force_int(version_parts[0])
                    minor_version = force_int(version_parts[1])

                    if major_version is None or minor_version is None:
                        return CheckResult.UNKNOWN

                    if major_version >= 14:
                        return CheckResult.PASSED
                    elif major_version == 13 and minor_version > 2:
                        return CheckResult.PASSED
                    elif major_version == 12 and minor_version > 6:
                        return CheckResult.PASSED
                    elif major_version == 11 and minor_version > 11:
                        return CheckResult.PASSED
                    elif major_version == 10 and minor_version > 16:
                        return CheckResult.PASSED
                    elif major_version == 9 and minor_version == 6:
                        # PostgreSQL pre 10 used following versioning major.major.minor
                        if len(version_parts) < 3:
                            return CheckResult.UNKNOWN

                        bugfix_version = force_int(version_parts[2])

                        if bugfix_version is None:
                            return CheckResult.UNKNOWN

                        if bugfix_version > 21:
                            return CheckResult.PASSED

                    # everything older is not recommended to use anyway
                    return CheckResult.FAILED
        elif conf.get("engine") == ["aurora-postgresql"]:
            self.evaluated_keys.append("engine_version")

            engine_version = conf.get("engine_version")
            if engine_version and isinstance(engine_version, list) and isinstance(engine_version[0], str):
                version_parts = engine_version[0].split(".")
                if len(version_parts) == 2:
                    major_version = force_int(version_parts[0])
                    minor_version = force_int(version_parts[1])

                    if major_version is None or minor_version is None:
                        return CheckResult.UNKNOWN

                    if major_version >= 12:
                        return CheckResult.PASSED
                    elif major_version == 11 and minor_version > 8:
                        return CheckResult.PASSED
                    elif major_version == 10 and minor_version > 13:
                        return CheckResult.PASSED

                    # older versions are not available for Aurora cluster
                    return CheckResult.FAILED

        # probably a non PostgreSQL instance or we couldn't render it correctly
        return CheckResult.UNKNOWN


check = RDSPostgreSQLLogFDWExtension()
