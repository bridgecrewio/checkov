from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck


class ElasticsearchDomainLogging(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure Elasticsearch Domain Logging is enabled"
        id = "CKV_AWS_84"
        supported_resources = ("AWS::Elasticsearch::Domain", "AWS::OpenSearchService::Domain")
        categories = (CheckCategories.ENCRYPTION,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get('Properties'):
            properties = conf.get('Properties')
            if properties.get("LogPublishingOptions"):
                options = conf.get("Properties", {}).get("LogPublishingOptions", {})
                for option in options.keys():
                    test = conf["Properties"]["LogPublishingOptions"][option]
                    if not isinstance(test, int) and 'Enabled' in test.keys():
                        if test["Enabled"]:
                            return CheckResult.PASSED
        return CheckResult.FAILED


check = ElasticsearchDomainLogging()
