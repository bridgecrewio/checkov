from typing import Any, Dict, List

from checkov.common.models.enums import CheckResult, CheckCategories
from checkov.terraform.checks.data.base_check import BaseDataCheck

# A filter only *allowlists* zone identity when it filters on one of these
# names. Other filter names (opt-in-status, zone-type, region-name) constrain
# zone *attributes* and still allow a newly-added zone to appear.
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
        Fails an aws_availability_zones data source unless it *allowlists* which
        zones are returned via an identity-based filter (name = "zone-name" or
        "zone-id"), producing a closed, deterministic set.

        Denylist-style arguments (exclude_names, exclude_zone_ids) do NOT pass:
        they only remove specific known zones, so a newly-added AZ that is not in
        the exclude list still leaks through -- the same silent-expansion risk the
        check exists to catch. Attribute-only constraints such as `state`,
        `all_availability_zones`, or a filter on opt-in-status likewise FAIL.

        :param conf: aws_availability_zones data source configuration
        :return: <CheckResult>
        """
        # Only an identity-based filter (zone-name / zone-id) allowlists which
        # zones are returned. exclude_names / exclude_zone_ids are denylists and
        # leave the set open to newly-added zones, so they do NOT satisfy the check.
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
