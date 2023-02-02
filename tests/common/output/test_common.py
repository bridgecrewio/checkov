import pytest

from checkov.common.output.common import compare_table_items_severity


def test_compare_cve_items_severity():
    # given
    cve = [
        {"id": "CVE-2016-6186", "severity": "medium", "fixed_version": "1.8.14"},
        {"id": "CVE-2016-7401", "severity": "high", "fixed_version": "1.8.15"},
        {"id": "CVE-2021-33203", "severity": "medium", "fixed_version": "2.2.24"},
        {"id": "CVE-2019-19844", "severity": "critical", "fixed_version": "1.11.27"},
    ]

    # when
    cve.sort(key=compare_table_items_severity, reverse=True)

    # then
    assert cve == [
        {"id": "CVE-2019-19844", "severity": "critical", "fixed_version": "1.11.27"},
        {"id": "CVE-2016-7401", "severity": "high", "fixed_version": "1.8.15"},
        {"id": "CVE-2016-6186", "severity": "medium", "fixed_version": "1.8.14"},
        {"id": "CVE-2021-33203", "severity": "medium", "fixed_version": "2.2.24"},
    ]


def test_compare_iac_items_severity():
    # given
    iac = [
        {"id": "BC_K8S_1", "severity": "medium"},
        {"id": "BC_K8S_2", "severity": "high"},
        {"id": "BC_K8S_3", "severity": "medium"},
        {"id": "BC_K8S_4", "severity": "critical"},
    ]

    # when
    iac.sort(key=compare_table_items_severity, reverse=True)

    # then
    assert iac == [
        {"id": "BC_K8S_4", "severity": "critical"},
        {"id": "BC_K8S_2", "severity": "high"},
        {"id": "BC_K8S_1", "severity": "medium"},
        {"id": "BC_K8S_3", "severity": "medium"}
    ]
