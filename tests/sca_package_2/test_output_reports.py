import json
import sys
import xml
import xml.dom.minidom
import os
from operator import itemgetter
from pathlib import Path
from typing import List
from unittest import mock

import pytest
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.csv import CSVSBOM, FILE_NAME_OSS_PACKAGES
from checkov.common.output.cyclonedx import CycloneDX
from checkov.common.output.sarif import Sarif

EXAMPLES_DIR = Path(__file__).parent / "examples"
OUTPUTS_DIR = Path(__file__).parent / "outputs"


def _get_deterministic_items_in_cyclonedx(pretty_xml_as_list: List[str]) -> List[str]:
    # the lines with the fields "serialNumber", "bom-ref" and "timestamp" contain some not-deterministic data (uuids,
    # timestamp). so we skip these lines by the first 'if when checking whether we get the expected results
    # in addition also the line that display the checkov version may be changeable, so we skip it as well
    # (in the second 'if')
    black_list_words = ["bom-ref", "serialNumber", "timestamp", "bom", "xml"]
    filtered_list = []
    for i, line in enumerate(pretty_xml_as_list):
        if not any(word in line for word in black_list_words):
            if i == 0 or not any(tool_name in pretty_xml_as_list[i - 1] for tool_name in
                                 ("<name>checkov</name>", "<name>cyclonedx-python-lib</name>")):
                filtered_list.append(line)
    return filtered_list


def test_console_output(mocker, sca_package_2_report):
    console_output = sca_package_2_report.print_console(False, False, None, None, False)

    # then

    assert console_output == "".join(
        [
            'sca_package scan results:\n',
            '\n',
            'Failed checks: 7, Skipped checks: 3\n',
            '\n',
            '\t/requirements.txt - CVEs Summary:\n',
            '\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n',
            '\t│ Total CVEs: 6        │ critical: 1          │ high: 2              │ medium: 1            │ low: 0               │ skipped: 2           │ Total Packages Used: │\n',
            '\t│                      │                      │                      │                      │                      │                      │ 0                    │\n',
            '\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n',
            '\t│ To fix 4/4 CVEs, go to your Prisma Cloud account                                                                                                               │\n',
            '\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n',
            "\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n",
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ flask                │ CVE-2018-1000656     │ HIGH                 │ 0.6                  │ 0.12.3               │ 0.12.3               │                      │\n',
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ django               │ CVE-2019-19844       │ CRITICAL             │ 1.2                  │ 1.11.27              │ 2.2.24               │                      │\n',
            '\t│                      │ CVE-2016-7401        │ HIGH                 │                      │ 1.8.15               │                      │                      │\n',
            '\t│                      │ CVE-2021-33203       │ MEDIUM               │                      │ 2.2.24               │                      │                      │\n',
            '\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n',
            "\n",
            "\t/requirements.txt - Licenses Statuses:\n",
            '\t┌────────────────────────────────┬────────────────────────────────┬────────────────────────────────┬────────────────────────────────────┐\n',
            "\t│ Package name                   │ Package version                │ Policy ID                      │ License                            │\n",
            '\t├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┼────────────────────────────────────┤\n',
            '\t│ flask                          │ 0.6                            │ BC_LIC_1                       │ DUMMY_OTHER_LICENSE                │\n',
            '\t└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┴────────────────────────────────────┘\n',
            "\n",
            "\t/path/to/go.sum - CVEs Summary:\n",
            '\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n',
            '\t│ Total CVEs: 2        │ critical: 0          │ high: 2              │ medium: 0            │ low: 0               │ skipped: 0           │ Total Packages Used: │\n',
            '\t│                      │                      │                      │                      │                      │                      │ 0                    │\n',
            '\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n',
            '\t│ To fix 2/2 CVEs, go to your Prisma Cloud account                                                                                                               │\n',
            '\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n',
            "\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n",
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ golang.org/x/crypto  │ CVE-2020-29652       │ HIGH                 │ v0.0.1               │ 0.0.2                │ 0.0.2                │                      │\n',
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ github.com/dgrijalva │ CVE-2020-26160       │ HIGH                 │ v3.2.0               │ 4.0.0rc1             │ 4.0.0rc1             │                      │\n',
            '\t│ /jwt-go              │                      │                      │                      │                      │                      │                      │\n',
            '\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n',

        ]
    )


def test_console_output_in_tty(mocker: MockerFixture, sca_package_2_report):
    # simulate a tty call by enforcing color
    mocker.patch.dict(os.environ, {"FORCE_COLOR": "True"})

    console_output = sca_package_2_report.print_console(False, False, None, None, False)

    # then
    assert console_output == "".join(
        [
            '\x1b[34msca_package scan results:\n',
            '\x1b[0m\x1b[36m\n',
            'Failed checks: 7, Skipped checks: 3\n',
            '\n',
            '\x1b[0m\t/requirements.txt - CVEs Summary:\n',
            '\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n',
            '\t│ Total CVEs: 6        │ critical: 1          │ high: 2              │ medium: 1            │ low: 0               │ skipped: 2           │ Total Packages Used: │\n',
            '\t│                      │                      │                      │                      │                      │                      │ 0                    │\n',
            '\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n',
            '\t│ To fix 4/4 CVEs, go to your Prisma Cloud account                                                                                                               │\n',
            '\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n',
            "\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n",
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ flask                │ CVE-2018-1000656     │ HIGH                 │ 0.6                  │ 0.12.3               │ 0.12.3               │                      │\n',
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ django               │ CVE-2019-19844       │ CRITICAL             │ 1.2                  │ 1.11.27              │ 2.2.24               │                      │\n',
            '\t│                      │ CVE-2016-7401        │ HIGH                 │                      │ 1.8.15               │                      │                      │\n',
            '\t│                      │ CVE-2021-33203       │ MEDIUM               │                      │ 2.2.24               │                      │                      │\n',
            '\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n',
            "\n",
            "\t/requirements.txt - Licenses Statuses:\n",
            '\t┌────────────────────────────────┬────────────────────────────────┬────────────────────────────────┬────────────────────────────────────┐\n',
            "\t│ Package name                   │ Package version                │ Policy ID                      │ License                            │\n",
            '\t├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┼────────────────────────────────────┤\n',
            '\t│ flask                          │ 0.6                            │ BC_LIC_1                       │ DUMMY_OTHER_LICENSE                │\n',
            '\t└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┴────────────────────────────────────┘\n',
            "\n",
            "\t/path/to/go.sum - CVEs Summary:\n",
            '\t┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐\n',
            '\t│ Total CVEs: 2        │ critical: 0          │ high: 2              │ medium: 0            │ low: 0               │ skipped: 0           │ Total Packages Used: │\n',
            '\t│                      │                      │                      │                      │                      │                      │ 0                    │\n',
            '\t├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┤\n',
            '\t│ To fix 2/2 CVEs, go to your Prisma Cloud account                                                                                                               │\n',
            '\t├──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┤\n',
            "\t│ Package              │ CVE ID               │ Severity             │ Current version      │ Root fixed version   │ Compliant version    │ Reachability         │\n",
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ golang.org/x/crypto  │ CVE-2020-29652       │ HIGH                 │ v0.0.1               │ 0.0.2                │ 0.0.2                │                      │\n',
            '\t├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤\n',
            '\t│ github.com/dgrijalva │ CVE-2020-26160       │ HIGH                 │ v3.2.0               │ 4.0.0rc1             │ 4.0.0rc1             │                      │\n',
            '\t│ /jwt-go              │                      │                      │                      │                      │                      │                      │\n',
            '\t└──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘\n',
        ]
    )


def test_get_cyclonedx_report(sca_package_2_report, tmp_path: Path):
    cyclonedx_reports = [sca_package_2_report]
    cyclonedx = CycloneDX(repo_id="bridgecrewio/example", reports=cyclonedx_reports)
    cyclonedx_output = cyclonedx.get_xml_output()
    pretty_xml_as_string = str(xml.dom.minidom.parseString(cyclonedx_output).toprettyxml())
    with open(os.path.join(OUTPUTS_DIR, "results_cyclonedx.xml")) as f_xml:
        expected_pretty_xml = f_xml.read()

    actual_pretty_xml_as_list = _get_deterministic_items_in_cyclonedx(pretty_xml_as_string.split("\n"))
    expected_pretty_xml_as_list = _get_deterministic_items_in_cyclonedx(expected_pretty_xml.split("\n"))

    assert actual_pretty_xml_as_list == expected_pretty_xml_as_list


def test_get_cyclonedx_report_with_licenses_with_comma(sca_package_report_2_with_comma_in_licenses, tmp_path: Path):
    cyclonedx_reports = [sca_package_report_2_with_comma_in_licenses]
    cyclonedx = CycloneDX(repo_id="bridgecrewio/example", reports=cyclonedx_reports)
    cyclonedx_output = cyclonedx.get_xml_output()

    pretty_xml_as_string = str(xml.dom.minidom.parseString(cyclonedx_output).toprettyxml())

    with open(os.path.join(OUTPUTS_DIR, "results_cyclonedx_with_comma_in_licenses.xml")) as f_xml:
        expected_pretty_xml = f_xml.read()

    actual_pretty_xml_as_list = _get_deterministic_items_in_cyclonedx(pretty_xml_as_string.split("\n"))
    expected_pretty_xml_as_list = _get_deterministic_items_in_cyclonedx(expected_pretty_xml.split("\n"))

    print(actual_pretty_xml_as_list)
    return

    assert actual_pretty_xml_as_list == expected_pretty_xml_as_list


def test_get_cyclonedx_json_report_with_licenses_with_comma(tmp_path: Path,
                                                            sca_package_report_2_with_comma_in_licenses):
    # given
    cyclonedx_reports = [sca_package_report_2_with_comma_in_licenses]
    cyclonedx = CycloneDX(repo_id="bridgecrewio/example", reports=cyclonedx_reports)

    #  when
    output = json.loads(cyclonedx.get_json_output())

    # then
    assert output["$schema"] == "http://cyclonedx.org/schema/bom-1.4.schema.json"
    assert len(output["components"]) == 8
    assert len(output["dependencies"]) == 8
    assert len(output["vulnerabilities"]) == 8

    assert sorted(output["components"], key=itemgetter("purl")) == sorted([
        {
            "type": "library",
            "bom-ref": "pkg:pypi/bridgecrewio/example/path/to/requirements.txt/django@1.2",
            "name": "django",
            "version": "1.2",
            "licenses": [{"license": {"name": "OSI_BDS"}}],
            "purl": "pkg:pypi/bridgecrewio/example/path/to/requirements.txt/django@1.2",
        },
        {
            "type": "library",
            "bom-ref": "pkg:pypi/bridgecrewio/example/path/to/requirements.txt/flask@0.6",
            "name": "flask",
            "version": "0.6",
            "licenses": [
                {"license": {"name": "DUMMY_OTHER_LICENSE, ANOTHER_DOMMY_LICENSE"}},
                {"license": {"name": "OSI_APACHE"}},
            ],
            "purl": "pkg:pypi/bridgecrewio/example/path/to/requirements.txt/flask@0.6",
        },
        {
            "type": "library",
            "bom-ref": "pkg:golang/bridgecrewio/example/path/to/go.sum/github.com/dgrijalva/jwt-go@v3.2.0",
            "name": "github.com/dgrijalva/jwt-go",
            "version": "v3.2.0",
            "licenses": [{"license": {"name": "Unknown"}}],
            "purl": "pkg:golang/bridgecrewio/example/path/to/go.sum/github.com/dgrijalva/jwt-go@v3.2.0",
        },
        {
            "type": "library",
            "bom-ref": "pkg:golang/bridgecrewio/example/path/to/go.sum/github.com/miekg/dns@v1.1.41",
            "name": "github.com/miekg/dns",
            "version": "v1.1.41",
            "licenses": [{"license": {"name": "Unknown"}}],
            "purl": "pkg:golang/bridgecrewio/example/path/to/go.sum/github.com/miekg/dns@v1.1.41",
        },
        {
            "type": "library",
            "bom-ref": "pkg:golang/bridgecrewio/example/path/to/go.sum/github.com/prometheus/client_model@v0.0.0-20190129233127-fd36f4220a90",
            "name": "github.com/prometheus/client_model",
            "version": "v0.0.0-20190129233127-fd36f4220a90",
            "licenses": [{"license": {"name": "Unknown"}}],
            "purl": "pkg:golang/bridgecrewio/example/path/to/go.sum/github.com/prometheus/client_model@v0.0.0-20190129233127-fd36f4220a90",
        },
        {
            "type": "library",
            "bom-ref": "pkg:golang/bridgecrewio/example/path/to/go.sum/golang.org/x/crypto@v0.0.1",
            "name": "golang.org/x/crypto",
            "version": "v0.0.1",
            "licenses": [{"license": {"name": "Unknown"}}],
            "purl": "pkg:golang/bridgecrewio/example/path/to/go.sum/golang.org/x/crypto@v0.0.1",
        },
        {
            "type": "library",
            "bom-ref": "pkg:pypi/bridgecrewio/example/path/to/requirements.txt/requests@2.26.0",
            "name": "requests",
            "version": "2.26.0",
            "licenses": [{"license": {"name": "OSI_APACHE"}}],
            "purl": "pkg:pypi/bridgecrewio/example/path/to/requirements.txt/requests@2.26.0",
        },
        {
            "type": "library",
            "bom-ref": "pkg:pypi/bridgecrewio/example/path/to/sub/requirements.txt/requests@2.26.0",
            "name": "requests",
            "version": "2.26.0",
            "licenses": [{"license": {"name": "OSI_APACHE"}}],
            "purl": "pkg:pypi/bridgecrewio/example/path/to/sub/requirements.txt/requests@2.26.0",
        },
    ], key=itemgetter("purl"))


def test_get_csv_report(sca_package_2_report, tmp_path: Path):
    csv_sbom_report = CSVSBOM()
    csv_sbom_report.add_report(report=sca_package_2_report, git_org="acme", git_repository="bridgecrewio/example")
    csv_sbom_report.persist_report_oss_packages(file_name=FILE_NAME_OSS_PACKAGES, is_api_key=True,
                                                output_path=str(tmp_path))
    output_file_path = tmp_path / FILE_NAME_OSS_PACKAGES
    csv_output = output_file_path.read_text()
    csv_output_str = csv_sbom_report.get_csv_output_packages(check_type=CheckType.SCA_PACKAGE)

    # then
    expected_csv_output = [
        'Package,Version,Path,Line(s),Git Org,Git Repository,Vulnerability,Severity,Description,Licenses,Fix Version,Registry URL,Root Package,Root Version',
        'django,1.2,/requirements.txt,,acme,bridgecrewio/example,CVE-2019-19844,CRITICAL,"Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)",OSI_BDS,1.11.27,https://pypi.python.org/,,',
        'django,1.2,/requirements.txt,,acme,bridgecrewio/example,CVE-2016-7401,HIGH,"The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies.",OSI_BDS,1.8.15,https://pypi.python.org/,,',
        'django,1.2,/requirements.txt,,acme,bridgecrewio/example,CVE-2021-33203,MEDIUM,"Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories.",OSI_BDS,2.2.24,https://pypi.python.org/,,',
        'flask,0.6,/requirements.txt,,acme,bridgecrewio/example,CVE-2018-1000656,HIGH,The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083.,"OSI_APACHE, DUMMY_OTHER_LICENSE",0.12.3,https://pypi.python.org/,,',
        'golang.org/x/crypto,v0.0.1,/path/to/go.sum,,acme,bridgecrewio/example,CVE-2020-29652,HIGH,A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.3 for Go allows remote attackers to cause a denial of service against SSH servers.,Unknown,0.0.2,,,',
        'github.com/dgrijalva/jwt-go,v3.2.0,/path/to/go.sum,,acme,bridgecrewio/example,CVE-2020-26160,HIGH,"jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\\""aud\\""] (which is allowed by the specification). Because the type assertion fails, \\""\\"" is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check.",Unknown,4.0.0rc1,,,',
        'django,1.2,/requirements.txt,,acme,bridgecrewio/example,CVE-2016-6186,MEDIUM,"Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function in contrib/admin/static/admin/js/admin/RelatedObjectLookups.js in Django before 1.8.14, 1.9.x before 1.9.8, and 1.10.x before 1.10rc1 allows remote attackers to inject arbitrary web script or HTML via vectors involving unsafe usage of Element.innerHTML.",OSI_BDS,1.8.14,https://pypi.python.org/,,',
        'flask,0.6,/requirements.txt,,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656.,"OSI_APACHE, DUMMY_OTHER_LICENSE",1.0,https://pypi.python.org/,,',
        'requests,2.26.0,/requirements.txt,,acme,bridgecrewio/example,,,,OSI_APACHE,N/A,https://pypi.python.org/,,',
        'github.com/miekg/dns,v1.1.41,/path/to/go.sum,,acme,bridgecrewio/example,,,,Unknown,N/A,,,',
        'github.com/prometheus/client_model,v0.0.0-20190129233127-fd36f4220a90,/path/to/go.sum,,acme,bridgecrewio/example,,,,Unknown,N/A,,,',
        'requests,2.26.0,/path/to/sub/requirements.txt,,acme,bridgecrewio/example,,,,OSI_APACHE,N/A,,,', '']
    csv_output_as_list = csv_output.split("\n")
    assert csv_output_as_list == expected_csv_output

    expected_csv_output_str = [
        'Package,Version,Path,Line(s),Git Org,Git Repository,Vulnerability,Severity,Description,Licenses,Fix Version,Registry URL,Root Package,Root Version',
        '"django",1.2,/requirements.txt,,acme,bridgecrewio/example,CVE-2019-19844,CRITICAL,"Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)","OSI_BDS",1.11.27,https://pypi.python.org/,,',
        '"django",1.2,/requirements.txt,,acme,bridgecrewio/example,CVE-2016-7401,HIGH,"The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies.","OSI_BDS",1.8.15,https://pypi.python.org/,,',
        '"django",1.2,/requirements.txt,,acme,bridgecrewio/example,CVE-2021-33203,MEDIUM,"Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories.","OSI_BDS",2.2.24,https://pypi.python.org/,,',
        '"flask",0.6,/requirements.txt,,acme,bridgecrewio/example,CVE-2018-1000656,HIGH,"The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083.","OSI_APACHE, DUMMY_OTHER_LICENSE",0.12.3,https://pypi.python.org/,,',
        '"golang.org/x/crypto",v0.0.1,/path/to/go.sum,,acme,bridgecrewio/example,CVE-2020-29652,HIGH,"A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.3 for Go allows remote attackers to cause a denial of service against SSH servers.","Unknown",0.0.2,,,',
        '"github.com/dgrijalva/jwt-go",v3.2.0,/path/to/go.sum,,acme,bridgecrewio/example,CVE-2020-26160,HIGH,"jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\\"aud\\"] (which is allowed by the specification). Because the type assertion fails, \\"\\" is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check.","Unknown",4.0.0rc1,,,',
        '"django",1.2,/requirements.txt,,acme,bridgecrewio/example,CVE-2016-6186,MEDIUM,"Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function in contrib/admin/static/admin/js/admin/RelatedObjectLookups.js in Django before 1.8.14, 1.9.x before 1.9.8, and 1.10.x before 1.10rc1 allows remote attackers to inject arbitrary web script or HTML via vectors involving unsafe usage of Element.innerHTML.","OSI_BDS",1.8.14,https://pypi.python.org/,,',
        '"flask",0.6,/requirements.txt,,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,"The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656.","OSI_APACHE, DUMMY_OTHER_LICENSE",1.0,https://pypi.python.org/,,',
        '"requests",2.26.0,/requirements.txt,,acme,bridgecrewio/example,,,"","OSI_APACHE",N/A,https://pypi.python.org/,,',
        '"github.com/miekg/dns",v1.1.41,/path/to/go.sum,,acme,bridgecrewio/example,,,"","Unknown",N/A,,,',
        '"github.com/prometheus/client_model",v0.0.0-20190129233127-fd36f4220a90,/path/to/go.sum,,acme,bridgecrewio/example,,,"","Unknown",N/A,,,',
        '"requests",2.26.0,/path/to/sub/requirements.txt,,acme,bridgecrewio/example,,,"","OSI_APACHE",N/A,,,',
        '']
    csv_output_str_as_list = csv_output_str.split("\n")
    assert csv_output_str_as_list == expected_csv_output_str


def test_sarif_output(sca_package_report_2_with_skip_scope_function):
    # The creation of sarif_json may change the input report. in order not to affect the other tests, we use
    # a report that is unique for the scope of the function

    # when
    sarif_output = Sarif(reports=[sca_package_report_2_with_skip_scope_function], tool="Checkov").json

    # then
    sarif_output["runs"][0]["tool"]["driver"]["version"] = "2.0.x"
    expected_sarif_json = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
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
                                "id": "DUMMY_OTHER_LICENSE_flask@0.6",
                                "name": "License DUMMY_OTHER_LICENSE - flask: 0.6",
                                "shortDescription": {
                                    "text": "License DUMMY_OTHER_LICENSE - flask: 0.6"
                                },
                                "fullDescription": {
                                    "text": "Package flask@0.6 has license DUMMY_OTHER_LICENSE"
                                },
                                "help": {
                                    "text": "SCA license\nResource: requirements.txt.flask"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                }
                            },
                            {
                                "id": "CVE-2019-19844_django@1.2",
                                "name": "CVE-2019-19844 - django: 1.2",
                                "shortDescription": {
                                    "text": "CVE-2019-19844 - django: 1.2"
                                },
                                "fullDescription": {
                                    "text": "Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)"
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: requirements.txt.django\nStatus: fixed in 3.0.1, 2.2.9, 1.11.27"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                },
                                "properties": {
                                    "security-severity": "9.8"
                                },
                                "helpUri": "https://nvd.nist.gov/vuln/detail/CVE-2019-19844"
                            },
                            {
                                "id": "CVE-2016-7401_django@1.2",
                                "name": "CVE-2016-7401 - django: 1.2",
                                "shortDescription": {
                                    "text": "CVE-2016-7401 - django: 1.2"
                                },
                                "fullDescription": {
                                    "text": "The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies."
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: requirements.txt.django\nStatus: fixed in 1.9.10, 1.8.15"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                },
                                "properties": {
                                    "security-severity": "7.5"
                                },
                                "helpUri": "https://nvd.nist.gov/vuln/detail/CVE-2016-7401"
                            },
                            {
                                "id": "CVE-2021-33203_django@1.2",
                                "name": "CVE-2021-33203 - django: 1.2",
                                "shortDescription": {
                                    "text": "CVE-2021-33203 - django: 1.2"
                                },
                                "fullDescription": {
                                    "text": "Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories."
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: requirements.txt.django\nStatus: fixed in 3.2.4, 3.1.12, 2.2.24"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                },
                                "properties": {
                                    "security-severity": "4.9"
                                },
                                "helpUri": "https://nvd.nist.gov/vuln/detail/CVE-2021-33203"
                            },
                            {
                                "id": "CVE-2018-1000656_flask@0.6",
                                "name": "CVE-2018-1000656 - flask: 0.6",
                                "shortDescription": {
                                    "text": "CVE-2018-1000656 - flask: 0.6"
                                },
                                "fullDescription": {
                                    "text": "The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083."
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: requirements.txt.flask\nStatus: fixed in 0.12.3"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                },
                                "properties": {
                                    "security-severity": "7.5"
                                },
                                "helpUri": "https://nvd.nist.gov/vuln/detail/CVE-2018-1000656"
                            },
                            {
                                "id": "CVE-2020-26160_github.com/dgrijalva/jwt-go@v3.2.0",
                                "name": "CVE-2020-26160 - github.com/dgrijalva/jwt-go: v3.2.0",
                                "shortDescription": {
                                    "text": "CVE-2020-26160 - github.com/dgrijalva/jwt-go: v3.2.0"
                                },
                                "fullDescription": {
                                    "text": "jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\\\"aud\\\"] (which is allowed by the specification). Because the type assertion fails, \\\"\\\" is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check."
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: path/to/go.sum.github.com/dgrijalva/jwt-go\nStatus: fixed in v4.0.0-preview1"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                },
                                "properties": {
                                    "security-severity": "7.7"
                                },
                                "helpUri": "https://nvd.nist.gov/vuln/detail/CVE-2020-26160"
                            },
                            {
                                "id": "OSI_BDS_django@1.2",
                                "name": "License OSI_BDS - django: 1.2",
                                "shortDescription": {
                                    "text": "License OSI_BDS - django: 1.2"
                                },
                                "fullDescription": {
                                    "text": "Package django@1.2 has license OSI_BDS"
                                },
                                "help": {
                                    "text": "SCA license\nResource: requirements.txt.django"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                }
                            },
                            {
                                "id": "CVE-2016-6186_django@1.2",
                                "name": "CVE-2016-6186 - django: 1.2",
                                "shortDescription": {
                                    "text": "CVE-2016-6186 - django: 1.2"
                                },
                                "fullDescription": {
                                    "text": "Cross-site scripting (XSS) vulnerability in the dismissChangeRelatedObjectPopup function in contrib/admin/static/admin/js/admin/RelatedObjectLookups.js in Django before 1.8.14, 1.9.x before 1.9.8, and 1.10.x before 1.10rc1 allows remote attackers to inject arbitrary web script or HTML via vectors involving unsafe usage of Element.innerHTML."
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: requirements.txt.django\nStatus: fixed in 1.9.8, 1.8.14"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                },
                                "properties": {
                                    "security-severity": "6.1"
                                },
                                "helpUri": "https://nvd.nist.gov/vuln/detail/CVE-2016-6186"
                            },
                            {
                                "id": "CVE-2019-1010083_flask@0.6",
                                "name": "CVE-2019-1010083 - flask: 0.6",
                                "shortDescription": {
                                    "text": "CVE-2019-1010083 - flask: 0.6"
                                },
                                "fullDescription": {
                                    "text": "The Pallets Project Flask before 1.0 is affected by: unexpected memory usage. The impact is: denial of service. The attack vector is: crafted encoded JSON data. The fixed version is: 1. NOTE: this may overlap CVE-2018-1000656."
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: requirements.txt.flask\nStatus: fixed in 1.0"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                },
                                "properties": {
                                    "security-severity": "7.5"
                                },
                                "helpUri": "https://nvd.nist.gov/vuln/detail/CVE-2019-1010083"
                            },
                            {
                                "id": "CVE-2020-29652_golang.org/x/crypto@v0.0.1",
                                "name": "CVE-2020-29652 - golang.org/x/crypto: v0.0.1",
                                "shortDescription": {
                                    "text": "CVE-2020-29652 - golang.org/x/crypto: v0.0.1"
                                },
                                "fullDescription": {
                                    "text": "A nil pointer dereference in the golang.org/x/crypto/ssh component through v0.0.3 for Go allows remote attackers to cause a denial of service against SSH servers."
                                },
                                "help": {
                                    "text": "SCA package scan\nResource: path/to/go.sum.golang.org/x/crypto\nStatus: fixed in v0.0.2"
                                },
                                "defaultConfiguration": {
                                    "level": "error"
                                },
                                "properties": {
                                    "security-severity": "7.5"
                                },
                                "helpUri": "https://nvd.nist.gov/vuln/detail/CVE-2020-29652"
                            }
                        ],
                        "organization": "bridgecrew"
                    }
                },
                "results": [
                    {
                        "ruleId": "DUMMY_OTHER_LICENSE_flask@0.6",
                        "ruleIndex": 0,
                        "level": "error",
                        "attachments": [],
                        "message": {
                            "text": "License DUMMY_OTHER_LICENSE - flask: 0.6"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "tests/sca_package_2/examples/requirements.txt"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "flask: 0.6"
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "CVE-2019-19844_django@1.2",
                        "ruleIndex": 1,
                        "level": "error",
                        "attachments": [],
                        "message": {
                            "text": "CVE-2019-19844 - django: 1.2"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "tests/sca_package_2/examples/requirements.txt"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "django: 1.2"
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "CVE-2016-7401_django@1.2",
                        "ruleIndex": 2,
                        "level": "error",
                        "attachments": [],
                        "message": {
                            "text": "CVE-2016-7401 - django: 1.2"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "tests/sca_package_2/examples/requirements.txt"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "django: 1.2"
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "CVE-2021-33203_django@1.2",
                        "ruleIndex": 3,
                        "level": "warning",
                        "attachments": [],
                        "message": {
                            "text": "CVE-2021-33203 - django: 1.2"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "tests/sca_package_2/examples/requirements.txt"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "django: 1.2"
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "CVE-2018-1000656_flask@0.6",
                        "ruleIndex": 4,
                        "level": "error",
                        "attachments": [],
                        "message": {
                            "text": "CVE-2018-1000656 - flask: 0.6"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "tests/sca_package_2/examples/requirements.txt"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "flask: 0.6"
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "CVE-2020-26160_github.com/dgrijalva/jwt-go@v3.2.0",
                        "ruleIndex": 5,
                        "level": "error",
                        "attachments": [],
                        "message": {
                            "text": "CVE-2020-26160 - github.com/dgrijalva/jwt-go: v3.2.0"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "path/to/go.sum"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "github.com/dgrijalva/jwt-go: v3.2.0"
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        "ruleId": "OSI_BDS_django@1.2",
                        "ruleIndex": 6,
                        "level": "warning",
                        "attachments": [],
                        "message": {
                            "text": "License OSI_BDS - django: 1.2"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "tests/sca_package_2/examples/requirements.txt"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "django: 1.2"
                                        }
                                    }
                                }
                            }
                        ],
                        "suppressions": [
                            {
                                "kind": "external",
                                "justification": "Test License suppression 1"
                            }
                        ]
                    },
                    {
                        "ruleId": "CVE-2016-6186_django@1.2",
                        "ruleIndex": 7,
                        "level": "warning",
                        "attachments": [],
                        "message": {
                            "text": "CVE-2016-6186 - django: 1.2"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "tests/sca_package_2/examples/requirements.txt"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "django: 1.2"
                                        }
                                    }
                                }
                            }
                        ],
                        "suppressions": [
                            {
                                "kind": "external",
                                "justification": "Test CVE suppression 2"
                            }
                        ]
                    },
                    {
                        "ruleId": "CVE-2019-1010083_flask@0.6",
                        "ruleIndex": 8,
                        "level": "error",
                        "attachments": [],
                        "message": {
                            "text": "CVE-2019-1010083 - flask: 0.6"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "tests/sca_package_2/examples/requirements.txt"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "flask: 0.6"
                                        }
                                    }
                                }
                            }
                        ],
                        "suppressions": [
                            {
                                "kind": "external",
                                "justification": "Test CVE suppression 1"
                            }
                        ]
                    },
                    {
                        "ruleId": "CVE-2020-29652_golang.org/x/crypto@v0.0.1",
                        "ruleIndex": 9,
                        "level": "error",
                        "attachments": [],
                        "message": {
                            "text": "CVE-2020-29652 - golang.org/x/crypto: v0.0.1"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": "path/to/go.sum"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "endLine": 1,
                                        "snippet": {
                                            "text": "golang.org/x/crypto: v0.0.1"
                                        }
                                    }
                                }
                            }
                        ],
                        "suppressions": [
                            {
                                "kind": "external",
                                "justification": "CVE-2020-29652 is skipped"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    assert sarif_output == expected_sarif_json


def test_get_junit_xml_string(sca_package_2_report_with_skip):
    # given
    report = sca_package_2_report_with_skip

    # when
    test_suites = [report.get_test_suite()]
    junit_xml_output = report.get_junit_xml_string(test_suites)

    expected_xml = xml.dom.minidom.parseString("""<?xml version="1.0" ?>
<testsuites disabled="0" errors="0" failures="5" tests="8" time="0.0">
	<testsuite disabled="0" errors="0" failures="5" name="sca_package scan" skipped="3" tests="8" time="0">
		<testcase name="[CRITICAL][CVE-2019-19844] django: 1.2" classname="/requirements.txt.django" file="/requirements.txt">
			<failure type="failure" message="SCA package scan">
Description: Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user\\'s email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)
Link: https://nvd.nist.gov/vuln/detail/CVE-2019-19844
Published Date: 2019-12-18T20:15:00+01:00
Base Score: 9.8
Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
Risk Factors: {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True}
Fix Details:
  Status: fixed in 3.0.1, 2.2.9, 1.11.27
  Fixed Version: 1.11.27

Resource: requirements.txt.django
File: /requirements.txt: 0-0

		0 | django: 1.2</failure>
		</testcase>
		<testcase name="[HIGH][CVE-2016-7401] django: 1.2" classname="/requirements.txt.django" file="/requirements.txt">
			<failure type="failure" message="SCA package scan">
Description: The cookie parsing code in Django before 1.8.15 and 1.9.x before 1.9.10, when used on a site with Google Analytics, allows remote attackers to bypass an intended CSRF protection mechanism by setting arbitrary cookies.
Link: https://nvd.nist.gov/vuln/detail/CVE-2016-7401
Published Date: 2016-10-03T20:59:00+02:00
Base Score: 7.5
Vector: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N
Risk Factors: {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True}
Fix Details:
  Status: fixed in 1.9.10, 1.8.15
  Fixed Version: 1.8.15

Resource: requirements.txt.django
File: /requirements.txt: 0-0

		0 | django: 1.2</failure>
		</testcase>
		<testcase name="[MEDIUM][CVE-2021-33203] django: 1.2" classname="/requirements.txt.django" file="/requirements.txt">
			<failure type="failure" message="SCA package scan">
Description: Django before 2.2.24, 3.x before 3.1.12, and 3.2.x before 3.2.4 has a potential directory traversal via django.contrib.admindocs. Staff members could use the TemplateDetailView view to check the existence of arbitrary files. Additionally, if (and only if) the default admindocs templates have been customized by application developers to also show file contents, then not only the existence but also the file contents would have been exposed. In other words, there is directory traversal outside of the template root directories.
Link: https://nvd.nist.gov/vuln/detail/CVE-2021-33203
Published Date: 2021-06-08T20:15:00+02:00
Base Score: 4.9
Vector: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N
Risk Factors: {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True}
Fix Details:
  Status: fixed in 3.2.4, 3.1.12, 2.2.24
  Fixed Version: 2.2.24

Resource: requirements.txt.django
File: /requirements.txt: 0-0

		0 | django: 1.2</failure>
		</testcase>
		<testcase name="[HIGH][CVE-2018-1000656] flask: 0.6" classname="/requirements.txt.flask" file="/requirements.txt">
			<failure type="failure" message="SCA package scan">
Description: The Pallets Project flask version Before 0.12.3 contains a CWE-20: Improper Input Validation vulnerability in flask that can result in Large amount of memory usage possibly leading to denial of service. This attack appear to be exploitable via Attacker provides JSON data in incorrect encoding. This vulnerability appears to have been fixed in 0.12.3. NOTE: this may overlap CVE-2019-1010083.
Link: https://nvd.nist.gov/vuln/detail/CVE-2018-1000656
Published Date: 2018-08-20T21:31:00+02:00
Base Score: 7.5
Vector: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H
Risk Factors: {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True}
Fix Details:
  Status: fixed in 0.12.3
  Fixed Version: 0.12.3

Resource: requirements.txt.flask
File: /requirements.txt: 0-0

		0 | flask: 0.6</failure>
		</testcase>
		<testcase name="[HIGH][CVE-2020-26160] github.com/dgrijalva/jwt-go: v3.2.0" classname="/path/to/go.sum.github.com/dgrijalva/jwt-go" file="/path/to/go.sum">
			<failure type="failure" message="SCA package scan">
Description: jwt-go before 4.0.0-preview1 allows attackers to bypass intended access restrictions in situations with []string{} for m[\&quot;aud\&quot;] (which is allowed by the specification). Because the type assertion fails, \&quot;\&quot; is the value of aud. This is a security problem if the JWT token is presented to a service that lacks its own audience check.
Link: https://nvd.nist.gov/vuln/detail/CVE-2020-26160
Published Date: 2020-09-30T20:15:00+02:00
Base Score: 7.7
Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
Risk Factors: {'Severity': 'Critical', 'HasFix': True, 'DoS': False, 'AttackComplexity': 'low', 'AttackVector': 'network', 'RemoteExecution': True}
Fix Details:
  Status: fixed in v4.0.0-preview1
  Fixed Version: 4.0.0rc1

Resource: path/to/go.sum.github.com/dgrijalva/jwt-go
File: /path/to/go.sum: 0-0

		0 | github.com/dgrijalva/jwt-go: v3.2.0</failure>
		</testcase>
		<testcase name="[MEDIUM][CVE-2016-6186] django: 1.2" classname="/requirements.txt.django" file="/requirements.txt">
			<skipped type="skipped" message="CVE-2016-6186 skipped for django: 1.2"/>
		</testcase>
		<testcase name="[HIGH][CVE-2019-1010083] flask: 0.6" classname="/requirements.txt.flask" file="/requirements.txt">
			<skipped type="skipped" message="CVE-2019-1010083 skipped for flask: 0.6"/>
		</testcase>
		<testcase name="[HIGH][CVE-2020-29652] golang.org/x/crypto: v0.0.1" classname="/path/to/go.sum.golang.org/x/crypto" file="/path/to/go.sum">
			<skipped type="skipped" message="CVE-2020-29652 skipped for golang.org/x/crypto: v0.0.1"/>
		</testcase>
	</testsuite>
</testsuites>

""")

    # then
    assert xml.dom.minidom.parseString(junit_xml_output).toprettyxml() == expected_xml.toprettyxml()
