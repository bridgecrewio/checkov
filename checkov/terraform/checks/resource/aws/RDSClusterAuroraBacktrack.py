from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class RDSClusterAuroraBacktrack(BaseResourceCheck):
    def __init__(self):
        """
        NIST.800-53.r5 CP-10, NIST.800-53.r5 CP-6, NIST.800-53.r5 CP-6(1), NIST.800-53.r5 CP-6(2), NIST.800-53.r5 CP-9,
        NIST.800-53.r5 SI-13(5)	Amazon Aurora clusters should have backtracking enabled
        """
        name = "Ensure that RDS Aurora Clusters have backtracking enabled"
        id = "CKV_AWS_326"
        supported_resources = ['aws_rds_cluster']
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):

        if conf.get("engine") and isinstance(conf.get("engine"), list):
            if len(conf.get("engine")) > 0:
                engine = conf.get("engine")[0]
                if engine in ["aurora", "aurora-mysql"]:
                    if RDSClusterAuroraBacktrack.backtracked(conf):
                        return CheckResult.PASSED
                    return CheckResult.FAILED
                return CheckResult.UNKNOWN
        if RDSClusterAuroraBacktrack.backtracked(conf):
            return CheckResult.PASSED
        return CheckResult.FAILED

    @staticmethod
    def backtracked(conf):
        if conf.get("backtrack_window") and isinstance(conf.get("backtrack_window"), list):
            if len(conf.get("backtrack_window")) > 0:
                if conf.get("backtrack_window")[0] > 0:
                    return True
        return False


check = RDSClusterAuroraBacktrack()
