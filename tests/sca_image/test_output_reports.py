import os.path
import sys
from pathlib import Path
import xml.dom.minidom
from typing import List

import pytest
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.csv import CSVSBOM
from checkov.common.output.cyclonedx import CycloneDX
from checkov.common.output.sarif import Sarif

EXAMPLES_DIR = Path(__file__).parent / "examples"
OUTPUTS_DIR = Path(__file__).parent / "outputs"


def _get_deterministic_items_in_cyclonedx(pretty_xml_as_list: List[str]) -> List[str]:
    # the lines with the fields "serialNumber", "bom-ref" and "timestamp" contain some not-deterministic data (uuids,
    # timestamp). so we skip these lines by the first 'if when checking whether we get the expected results
    # in addition also the line that display the checkov version may be changeable, so we skip it as well
    # (in the second 'if')
    filtered_list = []
    for i, line in enumerate(pretty_xml_as_list):
        if "bom-ref" not in line and "serialNumber" not in line and "timestamp" not in line:
            if i == 0 or not any(tool_name in pretty_xml_as_list[i - 1] for tool_name in
                                 ("<name>checkov</name>", "<name>cyclonedx-python-lib</name>")):
                filtered_list.append(line)
    return filtered_list


def test_console_output(mocker, sca_image_report):
    console_output = sca_image_report.print_console(False, False, None, None, False)
    assert console_output == "".join(
        [
            "sca_image scan results:\n",
            "\n",
            "Passed checks: 1, Failed checks: 3, Skipped checks: 1\n",
            "\n",
            "\t/path/to/Dockerfile (sha256:123456) - CVEs Summary:\n",
            '\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n',
            '\t│ Total CVEs: 3        │ critical: 0          │ high: 0              │ medium: 1            │ low: 1               │ skipped: 1           │ Total Packages Used: │\n',
            "\t│                      │                      │                      │                      │                      │                      │ 0                    │\n",
            '\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n',
            '\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n',
            '\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n',
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ perl                 │ CVE-2020-16156       │ MEDIUM               │ 5.34.0-3ubuntu1      │ N/A                  │ N/A                  │                      │\n',
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ pcre2                │ CVE-2022-1587        │ LOW                  │ 10.39-3build1        │ N/A                  │ N/A                  │                      │\n',
            '\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n',
            "\n",
            "\t/path/to/Dockerfile (sha256:123456) - Licenses Statuses:\n",
            '\t┌──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────────┐\n',
            '\t│ Package name             │ Package version          │ Policy ID                │ License                  │ Status                    │\n',
            '\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n',
            '\t│ perl                     │ 5.34.0-3ubuntu1          │ BC_LIC_1                 │ Apache-2.0-Fake          │ FAILED                    │\n',
            '\t└──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────────┘\n',
        ]
    )


def test_console_output_in_tty(mocker: MockerFixture, sca_image_report):
    # simulate a tty call by enforcing color
    mocker.patch.dict(os.environ, {"FORCE_COLOR": "True"})

    console_output = sca_image_report.print_console(False, False, None, None, False)

    # then
    assert console_output == "".join(
        [
            '\x1b[34msca_image scan results:\n',
            '\x1b[0m\x1b[36m\n',
            'Passed checks: 1, Failed checks: 3, Skipped checks: 1\n',
            '\n',
            '\x1b[0m\t/path/to/Dockerfile (sha256:123456) - CVEs Summary:\n',
            '\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n',
            '\t│ Total CVEs: 3        │ critical: 0          │ high: 0              │ medium: 1            │ low: 1               │ skipped: 1           │ Total Packages Used: │\n',
            "\t│                      │                      │                      │                      │                      │                      │ 0                    │\n",
            '\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n',
            '\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n',
            '\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n',
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ perl                 │ CVE-2020-16156       │ MEDIUM               │ 5.34.0-3ubuntu1      │ N/A                  │ N/A                  │                      │\n',
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ pcre2                │ CVE-2022-1587        │ LOW                  │ 10.39-3build1        │ N/A                  │ N/A                  │                      │\n',
            '\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n',
            '\n',
            '\t/path/to/Dockerfile (sha256:123456) - Licenses Statuses:\n',
            '\t┌──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────────┐\n',
            '\t│ Package name             │ Package version          │ Policy ID                │ License                  │ Status                    │\n',
            '\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼───────────────────────────┤\n',
            '\t│ perl                     │ 5.34.0-3ubuntu1          │ BC_LIC_1                 │ Apache-2.0-Fake          │ FAILED                    │\n',
            '\t└──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────────┘\n',
        ]
    )


def test_get_cyclonedx_report(sca_image_report, tmp_path: Path):
    cyclonedx_reports = [sca_image_report]
    cyclonedx = CycloneDX(repo_id="bridgecrewio/example", reports=cyclonedx_reports)
    cyclonedx_output = cyclonedx.get_xml_output()
    dom = xml.dom.minidom.parseString(cyclonedx_output)
    pretty_xml_as_string = str(dom.toprettyxml())
    with open(os.path.join(OUTPUTS_DIR, "results_cyclonedx.xml")) as f_xml:
        expected_pretty_xml = f_xml.read()

    actual_pretty_xml_as_list = _get_deterministic_items_in_cyclonedx(pretty_xml_as_string.split("\n"))
    expected_pretty_xml_as_list = _get_deterministic_items_in_cyclonedx(expected_pretty_xml.split("\n"))

    assert actual_pretty_xml_as_list == expected_pretty_xml_as_list


def test_get_csv_report(sca_image_report, tmp_path: Path):
    file_name = "container_images.csv"
    csv_sbom_report = CSVSBOM()
    csv_sbom_report.add_report(report=sca_image_report, git_org="acme", git_repository="bridgecrewio/example")
    csv_sbom_report.persist_report_container_images(file_name=file_name, is_api_key=True, output_path=str(tmp_path))
    output_file_path = tmp_path / file_name
    csv_output = output_file_path.read_text()
    csv_output_str = csv_sbom_report.get_csv_output_packages(check_type=CheckType.SCA_IMAGE)

    # # then
    expected_csv_output = [
        'Package,Version,Path,Line(s),Git Org,Git Repository,Vulnerability,Severity,Description,Licenses,Fix Version,Registry URL,Root Package,Root Version',
        'perl,5.34.0-3ubuntu1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,CVE-2020-16156,MEDIUM,CPAN 2.28 allows Signature Verification Bypass.,Apache-2.0-Fake,N/A,,,',
        'pcre2,10.39-3build1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,CVE-2022-1587,LOW,An out-of-bounds read vulnerability was discovered in the PCRE2 library in the get_recurse_data_length() function of the pcre2_jit_compile.c file. This issue affects recursions in JIT-compiled regular expressions caused by duplicate data transfers.,Apache-2.0,N/A,,,',
        'pcre2,10.39-3build1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,CVE-2022-1586,LOW,An out-of-bounds read vulnerability was discovered in the PCRE2 library in the compile_xclass_matchingpath() function of the pcre2_jit_compile.c file. This involves a unicode property matching issue in JIT-compiled regular expressions. The issue occurs because the character was not fully read in case-less matching within JIT.,Apache-2.0,N/A,,,',
        'bzip2,1.0.8-5build1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,,,,Unknown,N/A,,,',
        'libidn2,2.3.2-2build1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,,,,Unknown,N/A,,,', '']

    csv_output_as_list = csv_output.split("\n")
    assert csv_output_as_list == expected_csv_output

    expected_csv_output_str = [
        'Package,Version,Path,Line(s),Git Org,Git Repository,Vulnerability,Severity,Description,Licenses,Fix Version,Registry URL,Root Package,Root Version',
        '"perl",5.34.0-3ubuntu1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,CVE-2020-16156,MEDIUM,"CPAN 2.28 allows Signature Verification Bypass.","Apache-2.0-Fake",N/A,,,',
        '"pcre2",10.39-3build1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,CVE-2022-1587,LOW,"An out-of-bounds read vulnerability was discovered in the PCRE2 library in the get_recurse_data_length() function of the pcre2_jit_compile.c file. This issue affects recursions in JIT-compiled regular expressions caused by duplicate data transfers.","Apache-2.0",N/A,,,',
        '"pcre2",10.39-3build1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,CVE-2022-1586,LOW,"An out-of-bounds read vulnerability was discovered in the PCRE2 library in the compile_xclass_matchingpath() function of the pcre2_jit_compile.c file. This involves a unicode property matching issue in JIT-compiled regular expressions. The issue occurs because the character was not fully read in case-less matching within JIT.","Apache-2.0",N/A,,,',
        '"bzip2",1.0.8-5build1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,,,"","Unknown",N/A,,,',
        '"libidn2",2.3.2-2build1,/path/to/Dockerfile (sha256:123456),,acme,bridgecrewio/example,,,"","Unknown",N/A,,,',
        '']
    csv_output_str_as_list = csv_output_str.split("\n")
    assert csv_output_str_as_list == expected_csv_output_str


def test_sarif_output(sca_image_report_scope_function):
    # The creation of sarif_json may change the input report. in order not to affect the other tests, we use
    # a report that is unique for the scope of the function

    # given
    sarif_output = Sarif(reports=[sca_image_report_scope_function], tool="Checkov").json

    # then
    sarif_output["runs"][0]["tool"]["driver"]["version"] = "2.0.x"
    expected_sarif_json = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Checkov",
                        "version": "2.0.x",
                        "informationUri": "https://checkov.io",
                        "rules": [
                            {
                                "id": "Apache-2.0-Fake_perl@5.34.0-3ubuntu1",
                                "name": "License Apache-2.0-Fake - perl: 5.34.0-3ubuntu1",
                                "shortDescription": {"text": "License Apache-2.0-Fake - perl: 5.34.0-3ubuntu1"},
                                "fullDescription": {"text": "Package perl@5.34.0-3ubuntu1 has license Apache-2.0-Fake"},
                                "help": {"text": "SCA license\nResource: path/to/Dockerfile (sha256:123456).perl"},
                                "defaultConfiguration": {"level": "error"},
                            },
                            {
                                "id": "CVE-2020-16156_perl@5.34.0-3ubuntu1",
                                "name": "CVE-2020-16156 - perl: 5.34.0-3ubuntu1",
                                "shortDescription": {"text": "CVE-2020-16156 - perl: 5.34.0-3ubuntu1"},
                                "fullDescription": {"text": "CPAN 2.28 allows Signature Verification Bypass."},
                                "help": {
                                    "text": "SCA package scan\nResource: path/to/Dockerfile (sha256:123456).perl\nStatus: needed"
                                },
                                "defaultConfiguration": {"level": "error"},
                                "properties": {"security-severity": "7.8"},
                                "helpUri": "https://people.canonical.com/~ubuntu-security/cve/2020/CVE-2020-16156",
                            },
                            {
                                "id": "CVE-2022-1587_pcre2@10.39-3build1",
                                "name": "CVE-2022-1587 - pcre2: 10.39-3build1",
                                "shortDescription": {"text": "CVE-2022-1587 - pcre2: 10.39-3build1"},
                                "fullDescription": {
                                    "text": "An out-of-bounds read vulnerability was discovered in the PCRE2 library in the get_recurse_data_length() function of the pcre2_jit_compile.c file. This issue affects recursions in JIT-compiled regular expressions caused by duplicate data transfers."
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: path/to/Dockerfile (sha256:123456).pcre2\nStatus: needed"
                                },
                                "defaultConfiguration": {"level": "error"},
                                "properties": {"security-severity": "9.1"},
                                "helpUri": "https://people.canonical.com/~ubuntu-security/cve/2022/CVE-2022-1587",
                            },
                            {
                                "id": "CVE-2022-1586_pcre2@10.39-3build1",
                                "name": "CVE-2022-1586 - pcre2: 10.39-3build1",
                                "shortDescription": {"text": "CVE-2022-1586 - pcre2: 10.39-3build1"},
                                "fullDescription": {
                                    "text": "An out-of-bounds read vulnerability was discovered in the PCRE2 library in the compile_xclass_matchingpath() function of the pcre2_jit_compile.c file. This involves a unicode property matching issue in JIT-compiled regular expressions. The issue occurs because the character was not fully read in case-less matching within JIT."
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: path/to/Dockerfile (sha256:123456).pcre2\nStatus: needed"
                                },
                                "defaultConfiguration": {"level": "error"},
                                "properties": {"security-severity": "9.1"},
                                "helpUri": "https://people.canonical.com/~ubuntu-security/cve/2022/CVE-2022-1586",
                            },
                        ],
                        "organization": "bridgecrew",
                    }
                },
                "results": [
                    {
                        "ruleId": "Apache-2.0-Fake_perl@5.34.0-3ubuntu1",
                        "ruleIndex": 0,
                        "level": "error",
                        "attachments": [],
                        "message": {"text": "License Apache-2.0-Fake - perl: 5.34.0-3ubuntu1"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/Dockerfile"},
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {"text": "perl: 5.34.0-3ubuntu1"},
                                    },
                                }
                            }
                        ],
                    },
                    {
                        "ruleId": "CVE-2020-16156_perl@5.34.0-3ubuntu1",
                        "ruleIndex": 1,
                        "level": "warning",
                        "attachments": [],
                        "message": {"text": "CVE-2020-16156 - perl: 5.34.0-3ubuntu1"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/Dockerfile"},
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {"text": "perl: 5.34.0-3ubuntu1"},
                                    },
                                }
                            }
                        ],
                    },
                    {
                        "ruleId": "CVE-2022-1587_pcre2@10.39-3build1",
                        "ruleIndex": 2,
                        "level": "note",
                        "attachments": [],
                        "message": {"text": "CVE-2022-1587 - pcre2: 10.39-3build1"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/Dockerfile"},
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {"text": "pcre2: 10.39-3build1"},
                                    },
                                }
                            }
                        ],
                    },
                    {
                        "ruleId": "CVE-2022-1586_pcre2@10.39-3build1",
                        "ruleIndex": 3,
                        "level": "note",
                        "attachments": [],
                        "message": {"text": "CVE-2022-1586 - pcre2: 10.39-3build1"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {"uri": "path/to/Dockerfile"},
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {"text": "pcre2: 10.39-3build1"},
                                    },
                                }
                            }
                        ],
                        "suppressions": [{"kind": "external", "justification": "CVE-2022-1586 is skipped"}],
                    },
                ],
            }
        ],
    }

    assert sarif_output == expected_sarif_json


def test_get_junit_xml_string(sca_image_report):
    # given
    test_suites = [sca_image_report.get_test_suite()]

    #  when
    junit_xml_output = sca_image_report.get_junit_xml_string(test_suites)

    # then
    assert xml.dom.minidom.parseString(junit_xml_output).toprettyxml() == "\n".join(
        [
            '<?xml version="1.0" ?>',
            '<testsuites disabled="0" errors="0" failures="3" tests="5" time="0.0">',
            "\t",
            "\t",
            '\t<testsuite disabled="0" errors="0" failures="3" name="sca_image scan" skipped="1" tests="5" time="0">',
            "\t\t",
            "\t\t",
            '\t\t<testcase name="[NONE][BC_LIC_1] SCA license" classname="/path/to/Dockerfile (sha256:123456).path/to/Dockerfile (sha256:123456).pcre2" file="/path/to/Dockerfile (sha256:123456)"/>',
            "\t\t",
            "\t\t",
            '\t\t<testcase name="[NONE][BC_LIC_1] SCA license" classname="/path/to/Dockerfile (sha256:123456).path/to/Dockerfile (sha256:123456).perl" file="/path/to/Dockerfile (sha256:123456)">',
            "\t\t\t",
            "\t\t\t",
            '\t\t\t<failure type="failure" message="SCA license">',
            "Resource: path/to/Dockerfile (sha256:123456).perl",
            "File: /path/to/Dockerfile (sha256:123456): 0-0",
            "Guideline: None",
            "",
            "\t\t0 | perl: 5.34.0-3ubuntu1</failure>",
            "\t\t\t",
            "\t\t",
            "\t\t</testcase>",
            "\t\t",
            "\t\t",
            '\t\t<testcase name="[MEDIUM][CKV_CVE_2020_16156] SCA package scan" classname="/path/to/Dockerfile (sha256:123456).path/to/Dockerfile (sha256:123456).perl" file="/path/to/Dockerfile (sha256:123456)">',
            "\t\t\t",
            "\t\t\t",
            '\t\t\t<failure type="failure" message="SCA package scan">',
            "Resource: path/to/Dockerfile (sha256:123456).perl",
            "File: /path/to/Dockerfile (sha256:123456): 0-0",
            "Guideline: None",
            "",
            "\t\t0 | perl: 5.34.0-3ubuntu1</failure>",
            "\t\t\t",
            "\t\t",
            "\t\t</testcase>",
            "\t\t",
            "\t\t",
            '\t\t<testcase name="[LOW][CKV_CVE_2022_1587] SCA package scan" classname="/path/to/Dockerfile (sha256:123456).path/to/Dockerfile (sha256:123456).pcre2" file="/path/to/Dockerfile (sha256:123456)">',
            "\t\t\t",
            "\t\t\t",
            '\t\t\t<failure type="failure" message="SCA package scan">',
            "Resource: path/to/Dockerfile (sha256:123456).pcre2",
            "File: /path/to/Dockerfile (sha256:123456): 0-0",
            "Guideline: None",
            "",
            "\t\t0 | pcre2: 10.39-3build1</failure>",
            "\t\t\t",
            "\t\t",
            "\t\t</testcase>",
            "\t\t",
            "\t\t",
            '\t\t<testcase name="[LOW][CKV_CVE_2022_1586] SCA package scan" classname="/path/to/Dockerfile (sha256:123456).path/to/Dockerfile (sha256:123456).pcre2" file="/path/to/Dockerfile (sha256:123456)">',
            "\t\t\t",
            "\t\t\t",
            '\t\t\t<skipped type="skipped" message="CVE-2022-1586 is skipped"/>',
            "\t\t\t",
            "\t\t",
            "\t\t</testcase>",
            "\t\t",
            "\t",
            "\t</testsuite>",
            "\t",
            "",
            "</testsuites>",
            ""
        ]
    )
