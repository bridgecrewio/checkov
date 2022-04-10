from checkov.terraform.checks.resource.base_resource_value_check import BaseResourceValueCheck
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.common.models.consts import ANY_VALUE


class ElasticsearchDomainLogging(BaseResourceValueCheck):

    def __init__(self):
        name = "Ensure Elasticsearch Domain Logging is enabled"
        id = "CKV_AWS_84"
        supported_resources = ['aws_elasticsearch_domain', 'aws_opensearch_domain']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return "log_publishing_options/[0]/cloudwatch_log_group_arn"

    def scan_resource_conf(self, conf):
        if conf.get("log_publishing_options") and isinstance(conf.get("log_publishing_options"), list):
            option = conf.get("log_publishing_options")[0]
            if isinstance(option, dict) and option.get('cloudwatch_log_group_arn'):
                if option.get('enabled') == [False]:
                    self.evaluated_keys = ["log_publishing_options/[0]/enabled"]
                    return CheckResult.FAILED
            return CheckResult.PASSED
        self.evaluated_keys = ["log_publishing_options"]
        return CheckResult.FAILED

    def get_expected_value(self):
        return ANY_VALUE


check = ElasticsearchDomainLogging()
