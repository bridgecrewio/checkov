from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckCategories, CheckResult


class ElasticsearchDomainAuditLogging(BaseResourceCheck):

    def __init__(self):
        name = "Ensure Elasticsearch Domain Audit Logging is enabled"
        id = "CKV_AWS_317"
        supported_resources = ['aws_elasticsearch_domain', 'aws_opensearch_domain']
        categories = [CheckCategories.LOGGING]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf) -> CheckResult:
        if conf.get('log_publishing_options') and isinstance(conf.get('log_publishing_options'), list) and \
                len(conf.get('log_publishing_options')) > 0:
            options = conf.get('log_publishing_options')
            for option in options:
                if option.get('log_type') and isinstance(option.get('log_type'), list):
                    logtype = option.get('log_type')[0]
                    if logtype == "AUDIT_LOGS":
                        if option.get('enabled') and isinstance(option.get('enabled'), list):
                            enabled = option.get('enabled')[0]
                            if enabled:
                                return CheckResult.PASSED

        return CheckResult.FAILED


check = ElasticsearchDomainAuditLogging()
