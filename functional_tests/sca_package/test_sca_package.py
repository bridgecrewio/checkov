from pathlib import Path

from mock.mock import MagicMock
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.sca_package.runner import Runner
from checkov.common.output.csv import CSVSBOM

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_full_regular_case(mocker: MockerFixture, scan_result):
    # mocking
    bc_integration.bc_api_key = "abcd1234-abcd-1234-abcd-1234abcd1234"
    scanner_mock = MagicMock()
    scanner_mock.return_value.scan.return_value = scan_result
    mocker.patch("checkov.sca_package.runner.Scanner", side_effect=scanner_mock)

    ##############################################################################################################
    # phase 1: creating report (without asserting it, as it already happens in the UTs for sca_package's runner) #
    ##############################################################################################################
    report = Runner().run(root_folder=EXAMPLES_DIR)

    ####################################################
    # phase 2: creating cli output based on the report #
    ####################################################

    cli_output = report.print_console(False, False, None, None, False)

    assert cli_output == "\n".join(
        ['\x1b[34msca_package scan results:',
         '\x1b[0m\x1b[36m', 'Failed checks: 9, Skipped checks: 0',
         '',
         '\x1b[0m\t/path/to/requirements.txt - CVEs Summary:',
         '\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐',
         '\t│ Total CVEs: 6      │ critical: 1        │ high: 3            │ medium: 2          │ low: 0             │ skipped: 0         │',
         '\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤',
         '\t│ To fix 6/6 CVEs, go to https://www.bridgecrew.cloud/                                                                        │',
         '\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤',
         '\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ flask              │ CVE-2019-1010083   │ high               │ 0.6                │ 1.0                │ 1.0                │',
         '\t│                    │ CVE-2018-1000656   │ high               │                    │ 0.12.3             │                    │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ django             │ CVE-2019-19844     │ critical           │ 1.2                │ 1.11.27            │ 2.2.24             │',
         '\t│                    │ CVE-2016-7401      │ high               │                    │ 1.8.15             │                    │',
         '\t│                    │ CVE-2016-6186      │ medium             │                    │ 1.8.14             │                    │',
         '\t│                    │ CVE-2021-33203     │ medium             │                    │ 2.2.24             │                    │',
         '\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘',
         '',
         '\t/path/to/requirements.txt - Licenses Statuses:',
         '\t┌────────────────────────┬────────────────────────┬────────────────────────┬────────────────────────┬─────────────────────────┐',
         '\t│ Package name           │ Package version        │ Policy ID              │ License                │ Status                  │',
         '\t├────────────────────────┼────────────────────────┼────────────────────────┼────────────────────────┼─────────────────────────┤',
         '\t│ flask                  │ 0.6                    │ BC_LIC_1               │ DUMMY_OTHER_LICENSE    │ FAILED                  │',
         '\t└────────────────────────┴────────────────────────┴────────────────────────┴────────────────────────┴─────────────────────────┘',
         '',
         '\t/path/to/go.sum - CVEs Summary:',
         '\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐',
         '\t│ Total CVEs: 2      │ critical: 0        │ high: 2            │ medium: 0          │ low: 0             │ skipped: 0         │',
         '\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤',
         '\t│ To fix 2/2 CVEs, go to https://www.bridgecrew.cloud/                                                                        │',
         '\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤',
         '\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ golang.org/x/crypt │ CVE-2020-29652     │ high               │ v0.0.0-20200622213 │ v0.0.0-20201216223 │ v0.0.0-20201216223 │',
         '\t│ o                  │                    │                    │ 623-75b288015ac9   │ 049-8b5274cf687f   │ 049-8b5274cf687f   │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ github.com/dgrijal │ CVE-2020-26160     │ high               │ v3.2.0             │ 4.0.0rc1           │ 4.0.0rc1           │',
         '\t│ va/jwt-go          │                    │                    │                    │                    │                    │',
         '\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘',
         ''])

    ########################################################
    # phase 3: creating csv-bom report based on the report #
    ########################################################
    csv_sbom_report = CSVSBOM()
    csv_sbom_report.add_report(report=report, git_org="acme", git_repository="bridgecrewio/example")
    csv_output_str = csv_sbom_report.get_csv_output_packages(check_type=CheckType.SCA_PACKAGE)

    expected = ['Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses',
                '"django",1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2019-19844,CRITICAL,"OSI_BDS"',
                '"django",1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2016-6186,MEDIUM,"OSI_BDS"',
                '"django",1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2016-7401,HIGH,"OSI_BDS"',
                '"django",1.2,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2021-33203,MEDIUM,"OSI_BDS"',
                '"flask",0.6,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2019-1010083,HIGH,"OSI_APACHE, DUMMY_OTHER_LICENSE"',
                '"flask",0.6,/path/to/requirements.txt,acme,bridgecrewio/example,CVE-2018-1000656,HIGH,"OSI_APACHE, DUMMY_OTHER_LICENSE"',
                '"golang.org/x/crypto",v0.0.0-20200622213623-75b288015ac9,/path/to/go.sum,acme,bridgecrewio/example,CVE-2020-29652,HIGH,"Unknown"',
                '"github.com/dgrijalva/jwt-go",v3.2.0,/path/to/go.sum,acme,bridgecrewio/example,CVE-2020-26160,HIGH,"Unknown"',
                '"github.com/miekg/dns",v1.1.41,/path/to/go.sum,acme,bridgecrewio/example,,,"Unknown"',
                '"requests",2.26.0,/path/to/sub/requirements.txt,acme,bridgecrewio/example,,,"OSI_APACHE"',
                '"github.com/prometheus/client_model",v0.0.0-20190129233127-fd36f4220a90,/path/to/go.sum,acme,bridgecrewio/example,,,"Unknown"',
                '"requests",2.26.0,/path/to/requirements.txt,acme,bridgecrewio/example,,,"OSI_APACHE"', '']
    assert(sorted(csv_output_str.split("\n")) == sorted(expected))

    ##############################################################
    # phase 4: creating cyclonedx-bom report based on the report #
    ##############################################################

    # TBD
