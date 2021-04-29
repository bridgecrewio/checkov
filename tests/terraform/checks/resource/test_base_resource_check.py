import pytest

from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck


class TestStaticCheck(BaseResourceCheck):
    # for pytest not to collect this class as tests
    __test__ = False

    def __init__(self):
        name = "Test something"
        id = "CKV_TEST_1"
        supported_resources = ["ckv_test"]
        categories = [CheckCategories.CONVENTION]
        super().__init__(name=name, id=id, categories=categories, supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        if "check_result" in conf.keys():
            check_result = conf["check_result"][0]
            if check_result:
                return CheckResult.PASSED

            return CheckResult.FAILED

        return CheckResult.UNKNOWN


@pytest.mark.parametrize(
    "conf,expected",
    [
        ({"check_result": [True]}, CheckResult.PASSED),
        ({"check_result": [False]}, CheckResult.FAILED),
        ({"foo": ["bar"]}, CheckResult.UNKNOWN),
        ({"count": [0], "check_result": [True]}, CheckResult.UNKNOWN),
        ({"count": [1], "check_result": [True]}, CheckResult.PASSED),
    ],
    ids=["pass", "fail", "unknown", "count_zero", "count_one"],
)
def test_scan_entity_conf(conf, expected):
    result = TestStaticCheck().scan_entity_conf(conf, "ckv_test")

    assert result == expected
