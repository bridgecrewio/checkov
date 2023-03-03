from __future__ import annotations

from typing import Any

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class GKEBasicAuth(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure GKE basic auth is disabled"
        id = "CKV_GCP_19"
        supported_resources = ('google_container_cluster',)
        categories = (CheckCategories.KUBERNETES,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        # since GKE 1.19 the usage of basic auth is deprecated and in the provider version 4+ removed
        master_auth = conf.get("master_auth")
        if master_auth and isinstance(master_auth, list):
            username = master_auth[0].get('username')
            password = master_auth[0].get('password')
            if username or password:
                # only if both are set to the empty string it is fine
                # https://registry.terraform.io/providers/hashicorp/google/3.90.1/docs/resources/container_cluster.html
                if username and password:
                    if username[0] == '' and password[0] == '':
                        return CheckResult.PASSED
                return CheckResult.FAILED

        return CheckResult.PASSED

    def get_evaluated_keys(self) -> list[str]:
        return ['master_auth/[0]/username', 'master_auth/[0]/password']


check = GKEBasicAuth()
