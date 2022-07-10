from typing import Optional, Dict, Set

from checkov.common.output.record import Record


class GithubActionsRecord(Record):
    def __init__(self,
                 check_id,
                 check_name,
                 check_result,
                 code_block,
                 file_path,
                 file_line_range,
                 resource,
                 evaluations,
                 check_class,
                 file_abs_path,
                 entity_tags,
                 bc_check_id,
                 severity,
                 triggers: Optional[Set[str]],
                 jobs: Optional[Dict[str, Dict[str, int]]],
                 workflow_name: Optional[str]) -> None:
        super().__init__(check_id,
                         check_name,
                         check_result,
                         code_block,
                         file_path,
                         file_line_range,
                         resource,
                         evaluations,
                         check_class,
                         file_abs_path,
                         entity_tags,
                         bc_check_id,
                         severity,
                         )
        self.triggers = triggers,
        self.jobs = jobs,
        self.workflow_name = workflow_name
