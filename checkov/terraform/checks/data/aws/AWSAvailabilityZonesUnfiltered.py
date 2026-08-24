from typing import Any, Dict, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.data.base_check import BaseDataCheck

# A filter only pins zone *identity* when it filters on one of these names.
# Other filter names (opt-in-status, zone-type, region-name) constrain zone
# *attributes* and still allow a newly-added zone to appear.
IDENTITY_FILTER_NAMES = {"zone-name", "zone-id"}


class AWSAvailabilityZonesUnfiltered(BaseDataCheck):
    def __init__(self) -> None:
        name = (
            "Ensure aws_availability_zones data source pins zone identity so its "
            "result set does not silently expand when AWS adds an Availability Zone"
        )
        id = "CKV_AWS_394"
        supported_data = ["aws_availability_zones"]
        categories = [CheckCategories.GENERAL_SECURITY]
        super().__init__(name=name, id=id, categories=categories, supported_data=supported_data)

    def scan_data_conf(self, conf: Dict[str, List[Any]]) -> CheckResult:
        """
        Fails an aws_availability_zones data source unless it pins zone *identity*
        via exclude_names, exclude_zone_ids, or an identity-based filter
        (name = "zone-name" or "zone-id"). Attribute-only constraints such as
        `state`, `all_availability_zones`, or a filter on opt-in-status do NOT
        prevent a newly-added zone from appearing and therefore FAIL.

        :param conf: aws_availability_zones data source configuration
        :return: <CheckResult>
        """
        # exclude_names / exclude_zone_ids pin identity when set to a non-empty value.
        for identity_arg in ("exclude_names", "exclude_zone_ids"):
            values = conf.get(identity_arg)
            if values and values[0]:
                return CheckResult.PASSED

        # A filter pins identity only when it filters on zone-name / zone-id.
        filters = conf.get("filter", [])
        if not isinstance(filters, list):
            filters = [filters]

        for filter_block in filters:
            if isinstance(filter_block, dict):
                name = filter_block.get("name", [None])[0]
                if name in IDENTITY_FILTER_NAMES:
                    return CheckResult.PASSED

        return CheckResult.FAILED


check = AWSAvailabilityZonesUnfiltered()
