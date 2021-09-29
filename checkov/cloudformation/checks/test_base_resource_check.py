import unittest
from typing import Dict, Any

from checkov.cloudformation.checks.resource.base_resource_check import BaseResourceCheck
from checkov.common.models.enums import CheckResult


class TestBaseResourceCheck(unittest.TestCase):
    def test_base_check_accepts_variable_kwargs_for_future_proofing(self):
        class SubclassWithNewKwarg(BaseResourceCheck):
            def __init__(self):
                super().__init__(name="Example check", id="CKV_T_1", categories=[], supported_resources=["AWS::Any"],
                                 unused_kwarg="any")

            def scan_resource_conf(self, conf: Dict[str, Any], entity_type: str) -> CheckResult:
                pass

        SubclassWithNewKwarg()
