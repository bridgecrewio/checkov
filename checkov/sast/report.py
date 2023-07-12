from typing import Dict, Union

from checkov.common.output.report import Report


class SastReport(Report):

    def __init__(self, check_type: str, metadata: Dict[str, Union[str, int]], engine_name: str):
        super().__init__(check_type)
        self.metadata = metadata
        self.engine_name = engine_name

    def get_summary(self) -> Dict[str, Union[int, str]]:
        base_summary = super().get_summary()
        base_summary["engine_name"] = str(self.engine_name)
        base_summary = {**base_summary, **self.metadata}

        return base_summary
