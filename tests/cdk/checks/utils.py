from __future__ import annotations

import os
from pathlib import Path

from checkov.cdk.runner import CdkRunner
from checkov.runner_filter import RunnerFilter
from tests.cdk.checks.conftest import CHECK_ID_MAP


def run_check(check_name: str, lang: str) -> None:
    # setup sast runner
    runner = CdkRunner()
    runner.registry.temp_semgrep_rules_path = str(
        Path(__file__).parent / f"test_runner_temp_rules_{lang}.yaml"
    )

    # run actual check
    check_name_with_lang = f"{lang}_{check_name}"
    check_source_code = str(Path(__file__).parent / lang / check_name)
    reports = runner.run(
        root_folder=check_source_code,
        runner_filter=RunnerFilter(checks=CHECK_ID_MAP[check_name_with_lang]),
        external_checks_dir=[str(Path(__file__).parent.parent.parent / "checks" / lang)],
    )

    # get actual results
    assert len(reports) == 1
    report = reports[0]
    summary = report.get_summary()
    failed_checks = {check.file_path.lstrip("/") for check in report.failed_checks}

    # get expected results
    expected_to_fail_files, _ = get_expected_results_by_file_name(test_dir=check_source_code)
    expected_to_fail_count = extract_real_count_of_tests_by_filename(expected_to_fail_files)

    # check if results are correct
    assert summary["passed"] == 0
    assert summary["failed"] == expected_to_fail_count
    assert summary["skipped"] == 0
    assert summary["parsing_errors"] == 0

    assert failed_checks == set(expected_to_fail_files)


def get_expected_results_by_file_name(test_dir: str | Path) -> tuple[list[str], list[str]]:
    if not os.path.exists(test_dir):
        raise ValueError(f"test folder '{test_dir}' doesn't exist")
    expected_fail = []
    expected_pass = []
    for root, d_names, f_names in os.walk(test_dir):
        for file in f_names:
            if file.startswith('fail'):
                expected_fail.append(file)
            elif file.startswith('pass'):
                expected_pass.append(file)
            else:
                raise NameError('yaml test files should start with eiter pass / fail')

    return expected_fail, expected_pass


def extract_real_count_of_tests_by_filename(files: list[str]) -> int:
    """
    >>> extract_real_count_of_tests_by_filename(['fail.json', 'fail1.json'])
    2

    >>> extract_real_count_of_tests_by_filename(['fail__11__.json', 'fail2__11__.json', 'fail1.json'])
    23
    """
    total_count = 0
    for fn in files:
        name_parts = fn.split('__')
        if len(name_parts) == 3 and name_parts[1].isdigit():
            total_count += int(name_parts[1])
        else:
            total_count += 1
    return total_count
