from pathlib import Path

from checkov.runner_filter import RunnerFilter
from checkov.secrets.runner import Runner


def test_multiline_keyword_password_in_pod():
    # given
    test_file_path = Path(__file__).parent / "terraform_multiline/pod.tf"

    #  when
    report = Runner().run(
        root_folder=None, files=[str(test_file_path)], runner_filter=RunnerFilter(framework=["secrets"])
    )

    #  then
    failing_resources = {
        "dcbf46de362e1b6942054b89ee293984e9a8a40a",
        "ac236b0474a9a702f99dbe244a14548783ace5c5",
        "9ed4f1457a9c27dd868c1f21276c6d7098d2bacf",
        "06af723e58378574456be0b4c41a89194aaed0c3",
        "5db2fafebcfed9b4c9ffc570c46ef2ca94a3881a",
    }

    failed_check_resources = {c.resource for c in report.failed_checks}

    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == len(failing_resources)
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0

    assert failing_resources == failed_check_resources


def test_multiline_keyword_password_in_jsonencode():
    # given
    test_file_path = Path(__file__).parent / "terraform_multiline/ecs_jsonencode.tf"

    #  when
    report = Runner().run(
        root_folder=None, files=[str(test_file_path)], runner_filter=RunnerFilter(framework=["secrets"])
    )

    #  then
    failing_resources = {
        "dcbf46de362e1b6942054b89ee293984e9a8a40a",
        "ac236b0474a9a702f99dbe244a14548783ace5c5",
        "9ed4f1457a9c27dd868c1f21276c6d7098d2bacf",
        "06af723e58378574456be0b4c41a89194aaed0c3",
        "5db2fafebcfed9b4c9ffc570c46ef2ca94a3881a",
    }

    failed_check_resources = {c.resource for c in report.failed_checks}

    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == len(failing_resources)
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0

    assert failing_resources == failed_check_resources


def test_multiline_keyword_password_in_json_heredoc():
    # given
    test_file_path = Path(__file__).parent / "terraform_multiline/ecs_heredoc.tf"

    #  when
    report = Runner().run(
        root_folder=None, files=[str(test_file_path)], runner_filter=RunnerFilter(framework=["secrets"])
    )

    #  then
    failing_resources = {
        "dcbf46de362e1b6942054b89ee293984e9a8a40a",
        "ac236b0474a9a702f99dbe244a14548783ace5c5",
        "9ed4f1457a9c27dd868c1f21276c6d7098d2bacf",
        "06af723e58378574456be0b4c41a89194aaed0c3",
        "5db2fafebcfed9b4c9ffc570c46ef2ca94a3881a",
    }

    failed_check_resources = {c.resource for c in report.failed_checks}

    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == len(failing_resources)
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0

    assert failing_resources == failed_check_resources


def test_multiline_keyword_password_in_yaml_heredoc():
    # given
    test_file_path = Path(__file__).parent / "terraform_multiline/cfn_heredoc.tf"

    #  when
    report = Runner().run(
        root_folder=None, files=[str(test_file_path)], runner_filter=RunnerFilter(framework=["secrets"])
    )

    #  then
    failing_resources = {
        "dcbf46de362e1b6942054b89ee293984e9a8a40a",
        "ac236b0474a9a702f99dbe244a14548783ace5c5",
        "9ed4f1457a9c27dd868c1f21276c6d7098d2bacf",
        "06af723e58378574456be0b4c41a89194aaed0c3",
        "5db2fafebcfed9b4c9ffc570c46ef2ca94a3881a",
    }

    failed_check_resources = {c.resource for c in report.failed_checks}

    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == len(failing_resources)
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0

    assert failing_resources == failed_check_resources


def test_multiline_keyword_password_skip_data_blocks():
    # given
    test_file_path = Path(__file__).parent / "terraform_multiline/data.tf"

    #  when
    report = Runner().run(
        root_folder=None, files=[str(test_file_path)], runner_filter=RunnerFilter(framework=["secrets"])
    )

    #  then
    assert len(report.passed_checks) == 0
    assert len(report.failed_checks) == 0
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0
