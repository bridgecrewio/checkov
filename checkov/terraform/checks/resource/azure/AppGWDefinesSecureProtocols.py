from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

bad_ciphers = ['TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384',
               'TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256',
               'TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA',
               'TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA',
               'TLS_DHE_RSA_WITH_AES_256_GCM_SHA384',
               'TLS_DHE_RSA_WITH_AES_128_GCM_SHA256',
               'TLS_DHE_RSA_WITH_AES_256_CBC_SHA',
               'TLS_DHE_RSA_WITH_AES_128_CBC_SHA',
               'TLS_RSA_WITH_AES_256_GCM_SHA384',
               'TLS_RSA_WITH_AES_128_GCM_SHA256',
               'TLS_RSA_WITH_AES_256_CBC_SHA256',
               'TLS_RSA_WITH_AES_128_CBC_SHA256',
               'TLS_RSA_WITH_AES_256_CBC_SHA',
               'TLS_RSA_WITH_AES_128_CBC_SHA',
               'TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384 ',
               'TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256',
               'TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA',
               'TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA',
               'TLS_DHE_DSS_WITH_AES_256_CBC_SHA256',
               'TLS_DHE_DSS_WITH_AES_128_CBC_SHA256 ',
               'TLS_DHE_DSS_WITH_AES_256_CBC_SHA',
               'TLS_DHE_DSS_WITH_AES_128_CBC_SHA',
               'TLS_RSA_WITH_3DES_EDE_CBC_SHA',
               'TLS_DHE_DSS_WITH_3DES_EDE_CBC_SHA']


class AppGWDefinesSecureProtocols(BaseResourceCheck):
    def __init__(self):

        """
        https://azure.github.io/PSRule.Rules.Azure/en/rules/Azure.AppGw.SSLPolicy/

        """
        name = "Ensure Application Gateway defines secure protocols for in transit communication"
        id = "CKV_AZURE_218"
        supported_resources = ['azurerm_application_gateway']
        categories = [CheckCategories.ENCRYPTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if conf.get("ssl_policy") and isinstance(conf.get("ssl_policy"), list):
            ssl_policy = conf.get("ssl_policy")[0]
            if isinstance(ssl_policy.get("policy_type"), list) and ssl_policy.get("policy_type")[0]:
                if ssl_policy.get("policy_type")[0] != "Predefined":
                    if isinstance(ssl_policy.get("min_protocol_version"), list) \
                            and ssl_policy.get("min_protocol_version")[0] in ["TLSv1_2", "TLSv1_3"]:
                        ciphers = ssl_policy.get("cipher_suites")[0]
                        for cipher in ciphers:
                            if cipher in bad_ciphers:
                                return CheckResult.FAILED
                        return CheckResult.PASSED
                if isinstance(ssl_policy.get("policy_name"), list) \
                        and ssl_policy.get("policy_name")[0] == "AppGwSslPolicy20220101S":
                    return CheckResult.PASSED
                return CheckResult.FAILED
        return CheckResult.FAILED


check = AppGWDefinesSecureProtocols()
