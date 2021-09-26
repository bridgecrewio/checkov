from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class GoogleBigQueryDatasetPublicACL(BaseResourceCheck):
    def __init__(self):
        name = "Ensure that BigQuery datasets are not anonymously or publicly accessible"
        id = "CKV_GCP_15"
        supported_resources = ["google_bigquery_dataset"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        """
            Looks for ACL configuration at bigquery_dataset:
            https://www.terraform.io/docs/providers/google/r/bigquery_dataset.html#access
        :param conf: bigquery_dataset configuration
        :return: <CheckResult>
        """
        if "access" in conf.keys():
            for access in conf["access"]:
                if "special_group" in access:
                    if access["special_group"] in [["allAuthenticatedUsers"], ["allUsers"]]:
                        self.evaluated_keys = [f'access/[{conf["access"].index(access)}]/special_group']
                        return CheckResult.FAILED
                # access block with only the role key found in the statefile
                # when manually adding "allUsers" to the dataset
                elif not any(key in access for key in ["user_by_email", "group_by_email", "domain", "view"]):
                    self.evaluated_keys = [f'access/[{conf["access"].index(access)}]']
                    return CheckResult.FAILED
            self.evaluated_keys = ['access']
        return CheckResult.PASSED


check = GoogleBigQueryDatasetPublicACL()
