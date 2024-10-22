from typing import Dict, List, Any

from checkov.common.util.type_forcers import force_int

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

ASYMMETRIC_KEYS = {"ASYMMETRIC_DECRYPT", "ASYMMETRIC_SIGN"}
# rotation_period time unit is seconds
ONE_DAY = 24 * 60 * 60
NINETY_DAYS = 90 * ONE_DAY


class GoogleKMSKeyRotationPeriod(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure KMS encryption keys are rotated within a period of 90 days"
        id = "CKV_GCP_43"
        supported_resources = ("google_kms_crypto_key",)
        categories = (CheckCategories.GENERAL_SECURITY,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        purpose = conf.get("purpose")
        if purpose and isinstance(purpose, list) and purpose[0] in ASYMMETRIC_KEYS:
            # https://cloud.google.com/kms/docs/key-rotation#asymmetric
            # automatic key rotation is not supported for asymmetric keys
            return CheckResult.UNKNOWN

        self.evaluated_keys = ["rotation_period"]
        rotation = conf.get("rotation_period")
        if rotation and rotation[0] and isinstance(rotation[0], str):
            time = force_int(rotation[0][:-1])
            if time and ONE_DAY <= time <= NINETY_DAYS:
                return CheckResult.PASSED
        return CheckResult.FAILED


check = GoogleKMSKeyRotationPeriod()
