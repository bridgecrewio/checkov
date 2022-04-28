from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories

class ObjectStorageBucketPublicAccess(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure storage bucket does not have public access permissions."
        id = "CKV_YC_17"
        categories = [CheckCategories.GENERAL_SECURITY]
        supported_resources = ["yandex_storage_bucket"]
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf):
        if 'acl' in conf.keys():
            acl_block = conf['acl']
            if acl_block in [["public-read"], ["public-read-write"]]:
                return CheckResult.FAILED
        if 'grant' in conf.keys():
            grant_uri_block = conf['grant'][0]['uri']
            if grant_uri_block == ["http://acs.amazonaws.com/groups/global/AllUsers"]:
                return CheckResult.FAILED
        return CheckResult.PASSED

scanner = ObjectStorageBucketPublicAccess()