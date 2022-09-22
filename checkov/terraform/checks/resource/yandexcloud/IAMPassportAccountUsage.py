from __future__ import annotations

from typing import Any

from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult, CheckCategories


class IAMPassportAccountUsage(BaseResourceCheck):
    def __init__(self) -> None:
        name = "Ensure passport account is not used for assignment. Use service accounts and federated accounts where possible."
        id = "CKV_YC_24"
        categories = (CheckCategories.IAM,)
        supported_resources = (
            "yandex_resourcemanager_folder_iam_binding",
            "yandex_resourcemanager_folder_iam_member",
            "yandex_resourcemanager_cloud_iam_binding",
            "yandex_resourcemanager_cloud_iam_member",
            "yandex_organizationmanager_organization_iam_binding",
            "yandex_organizationmanager_organization_iam_member",
        )
        super().__init__(
            name=name,
            id=id,
            categories=categories,
            supported_resources=supported_resources,
        )

    def scan_resource_conf(self, conf: dict[str, list[Any]]) -> CheckResult:
        if self.entity_type == "yandex_resourcemanager_folder_iam_binding":
            for member in conf["members"][0]:
                if member.startswith("userAccount"):
                    return CheckResult.FAILED
            return CheckResult.PASSED
        if self.entity_type == "yandex_resourcemanager_folder_iam_member":
            if conf["member"][0].startswith("userAccount"):
                return CheckResult.FAILED
        if self.entity_type == "yandex_resourcemanager_cloud_iam_binding":
            for member in conf["members"][0]:
                if member.startswith("userAccount"):
                    return CheckResult.FAILED
            return CheckResult.PASSED
        if self.entity_type == "yandex_resourcemanager_cloud_iam_member":
            if conf["member"][0].startswith("userAccount"):
                return CheckResult.FAILED
        if self.entity_type == "yandex_organizationmanager_organization_iam_binding":
            for member in conf["members"][0]:
                if member.startswith("userAccount"):
                    return CheckResult.FAILED
            return CheckResult.PASSED
        if self.entity_type == "yandex_organizationmanager_organization_iam_member":
            if conf["member"][0].startswith("userAccount"):
                return CheckResult.FAILED
        return CheckResult.PASSED


scanner = IAMPassportAccountUsage()
