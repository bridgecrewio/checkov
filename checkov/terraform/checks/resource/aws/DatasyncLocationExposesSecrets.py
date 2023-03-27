from __future__ import annotations

from typing import Any

from checkov.common.models.consts import ANY_VALUE
from checkov.common.models.enums import CheckCategories
from checkov.terraform.checks.resource.base_resource_negative_value_check import BaseResourceNegativeValueCheck


class DatasyncLocationExposesSecrets(BaseResourceNegativeValueCheck):
    def __init__(self) -> None:
        name = "Ensure DataSync Location Object Storage doesn't expose secrets"
        id = "CKV_AWS_295"
        supported_resources = ("aws_datasync_location_object_storage",)
        categories = (CheckCategories.SECRETS,)
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def get_inspected_key(self) -> str:
        return "secret_key"

    def get_forbidden_values(self) -> list[Any]:
        return [ANY_VALUE]


check = DatasyncLocationExposesSecrets()
