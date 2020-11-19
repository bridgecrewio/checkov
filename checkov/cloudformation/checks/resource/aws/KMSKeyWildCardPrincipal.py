from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.cloudformation.checks.resource.base_resource_value_check import BaseResourceValueCheck


def get_recursively(search_dict, field):
    """
    Takes a dict with nested lists and dicts,
    and searches all dicts for a key of the field
    provided.
    """
    fields_found = []

    for key, value in search_dict.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_recursively(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found


class KMSKeyWildCardPrincipal(BaseResourceValueCheck):
    def __init__(self):
        name = "Ensure KMS key policy does not contain wildcard (*) principal"
        id = "CKV_AWS_33"
        supported_resources = ['AWS::KMS::Key']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self):
        return 'Properties/KeyPolicy/Statement/Principal'

    def scan_resource_conf(self, conf):
        if conf.get('Properties'):
            if conf['Properties'].get('KeyPolicy'):
                policy_block = conf['Properties']['KeyPolicy']
                principals_list = get_recursively(policy_block, 'Principal')
                for principal in principals_list:
                    if isinstance(principal, dict):
                        for principal_key, principal_value in principal.items():
                            if principal_value == '*':
                                return CheckResult.FAILED
                    else:
                        if principal == '*':
                            return CheckResult.FAILED

        return CheckResult.PASSED


check = KMSKeyWildCardPrincipal()
