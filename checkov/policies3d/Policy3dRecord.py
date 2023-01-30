from typing import List, Dict, Any

from checkov.common.output.record import Record


class Policy3dRecord(Record):
    def __init__(self,
                 check_id,
                 bc_check_id,
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
                 severity,
                 vulnerabilities: List[Dict[str, Any]]
                 ) -> None:
        super().__init__(
            check_id=check_id,
            bc_check_id=bc_check_id,
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
            severity=severity,
        )
        self.vulnerabilities = vulnerabilities
