from typing import List

from checkov.common.output.record import Record


def _filter_reports_for_incident_ids(failed_checks: List[Record], policy_names: List[str]) \
        -> List[Record]:
    return [failed_check for failed_check in failed_checks if failed_check.check_id in policy_names]
