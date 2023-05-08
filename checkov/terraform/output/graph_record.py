from typing import Any, Optional

from checkov.common.output.graph_record import GraphRecord
from checkov.common.output.record import Record
from checkov.terraform.output.origin_module_metadata import OriginModuleMetadata


class TerraformGraphRecord(GraphRecord):
    def __init__(self, record: Record, breadcrumbs: dict[str, dict[str, Any]],
                 origin_modules_metadata: Optional[list[OriginModuleMetadata]]) -> None:
        super().__init__(record, breadcrumbs)
        self.origin_modules_metadata = origin_modules_metadata
