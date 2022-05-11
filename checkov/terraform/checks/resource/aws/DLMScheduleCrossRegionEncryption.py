from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class DLMScheduleCrossRegionEncryption(BaseResourceCheck):
    def __init__(self):
        name = "Ensure DLM cross region schedules are encrypted"
        id = "CKV_AWS_255"
        supported_resources = ['aws_dlm_lifecycle_policy']
        categories = [CheckCategories.BACKUP_AND_RECOVERY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("policy_details") and isinstance(conf.get("policy_details"), list):
            policy = conf.get("policy_details")[0]

            if policy.get("schedule") and isinstance(policy.get("schedule"), list):
                schedules = policy.get("schedule")
                for idx, schedule in enumerate(schedules):
                    if schedule.get("cross_region_copy_rule") and isinstance(schedule.get("cross_region_copy_rule"), list):
                        for c_idx, cross_schedule_rule in enumerate(schedule.get("cross_region_copy_rule")):
                            if isinstance(cross_schedule_rule, dict) and cross_schedule_rule.get("encrypted") != [True]:
                                self.evaluated_keys = [
                                    f"policy_details/schedule/{idx}/cross_region_copy_rule/{c_idx}/encrypted"]
                                return CheckResult.FAILED
                        return CheckResult.PASSED
        return CheckResult.UNKNOWN


check = DLMScheduleCrossRegionEncryption()
