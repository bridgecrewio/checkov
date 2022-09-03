import xml
from pathlib import Path

from mock.mock import MagicMock
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.platform_integration import bc_integration
from checkov.runner_filter import RunnerFilter
from checkov.sca_package.runner import Runner
from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.output.csv import CSVSBOM

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_console_output(sca_image_report):
    console_output = sca_image_report.print_console(False, False, None, None, False)

    # then
    assert console_output == "\n".join(
        ['\x1b[34msca_image scan results:', '\x1b[0m\x1b[36m', 'Passed checks: 1, Failed checks: 3, Skipped checks: 1',
         '',
         '\x1b[0m\t/path/to/Dockerfile (sha256:123456) - CVEs Summary:',
         '\t┌────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐',
         '\t│ Total CVEs: 3      │ critical: 0        │ high: 0            │ medium: 1          │ low: 1             │ skipped: 1         │',
         '\t├────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┤',
         '\t├────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┤',
         '\t│ Package            │ CVE ID             │ Severity           │ Current version    │ Fixed version      │ Compliant version  │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ perl               │ CVE-2020-16156     │ medium             │ 5.34.0-3ubuntu1    │ N/A                │ N/A                │',
         '\t├────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤',
         '\t│ pcre2              │ CVE-2022-1587      │ low                │ 10.39-3build1      │ N/A                │ N/A                │',
         '\t└────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘',
         '',
         '\t/path/to/Dockerfile (sha256:123456) - Licenses Statuses:',
         '\t┌────────────────────────┬────────────────────────┬────────────────────────┬────────────────────────┬─────────────────────────┐',
         '\t│ Package name           │ Package version        │ Policy ID              │ License                │ Status                  │',
         '\t├────────────────────────┼────────────────────────┼────────────────────────┼────────────────────────┼─────────────────────────┤',
         '\t│ perl                   │ 5.34.0-3ubuntu1        │ BC_LIC_1               │ Apache-2.0-Fake        │ FAILED                  │',
         '\t└────────────────────────┴────────────────────────┴────────────────────────┴────────────────────────┴─────────────────────────┘',
         '']

    )


def test_get_csv_report(sca_image_report, tmp_path: Path):
    file_name = "container_images.csv"
    csv_sbom_report = CSVSBOM()
    csv_sbom_report.add_report(report=sca_image_report, git_org="acme", git_repository="bridgecrewio/example")
    csv_sbom_report.persist_report_container_images(file_name=file_name, is_api_key=True, output_path=str(tmp_path))
    output_file_path = tmp_path / file_name
    csv_output = output_file_path.read_text()
    csv_output_str = csv_sbom_report.get_csv_output_packages(check_type=CheckType.SCA_IMAGE)

    # # then
    expected_csv_output = ['Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses',
                           'perl,5.34.0-3ubuntu1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,CVE-2020-16156,MEDIUM,Apache-2.0-Fake',
                           'pcre2,10.39-3build1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,CVE-2022-1587,LOW,Apache-2.0',
                           'pcre2,10.39-3build1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,CVE-2022-1586,LOW,Apache-2.0',
                           'libidn2,2.3.2-2build1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,,,Unknown',
                           'bzip2,1.0.8-5build1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,,,Unknown',
                           '']
    csv_output_as_list = csv_output.split("\n")
    # the order is not the same always. making sure the header is at the same row
    assert csv_output_as_list[0] == expected_csv_output[0]
    assert set(csv_output_as_list) == set(expected_csv_output)

    expected_csv_output_str = ['Package,Version,Path,Git Org,Git Repository,Vulnerability,Severity,Licenses',
                               '"perl",5.34.0-3ubuntu1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,CVE-2020-16156,MEDIUM,"Apache-2.0-Fake"',
                               '"pcre2",10.39-3build1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,CVE-2022-1587,LOW,"Apache-2.0"',
                               '"pcre2",10.39-3build1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,CVE-2022-1586,LOW,"Apache-2.0"',
                               '"libidn2",2.3.2-2build1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,,,"Unknown"',
                               '"bzip2",1.0.8-5build1,/path/to/Dockerfile (sha256:123456),acme,bridgecrewio/example,,,"Unknown"',
                               '']
    csv_output_str_as_list = csv_output_str.split("\n")
    # the order is not the same always. making sure the header is at the same row
    assert csv_output_str_as_list[0] == expected_csv_output_str[0]
    assert set(csv_output_str_as_list) == set(expected_csv_output_str)
