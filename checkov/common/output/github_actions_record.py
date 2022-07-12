from typing import Optional, Dict, Set, List, Tuple, Any, Union

from checkov.common.bridgecrew.severities import Severity
from checkov.common.output.record import Record
from checkov.common.typing import _CheckResult


class GithubActionsRecord(Record):
    def __init__(self,
                 triggers: Optional[Set[str]],
                 job: Union[Optional[str], None],
                 workflow_name: Optional[str],
                 check_id: str,
                 check_name: str,
                 check_result: _CheckResult,
                 code_block: List[Tuple[int, str]],
                 file_path: str,
                 file_line_range: List[int],
                 resource: str,
                 evaluations: Optional[Dict[str, Any]],
                 check_class: str,
                 file_abs_path: str,
                 entity_tags: Optional[Dict[str, str]] = None,
                 bc_check_id: Optional[str] = None,
                 severity: Optional[Severity] = None,
                 ) -> None:
        super().__init__(check_id=check_id,
                         check_name=check_name,
                         check_result=check_result,
                         code_block=code_block,
                         file_path=file_path,
                         file_line_range=file_line_range,
                         resource=resource,
                         evaluations=evaluations,
                         check_class=check_class,
                         file_abs_path=file_abs_path,
                         entity_tags=entity_tags,
                         bc_check_id=bc_check_id,
                         severity=severity,
                         )
        self.triggers = triggers,
        self.job = job,
        self.workflow_name = workflow_name
