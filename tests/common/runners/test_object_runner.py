import pytest

from checkov.common.runners.object_runner import Runner


def test_get_start_and_end_lines():
    keys = ['jobs.*.steps[].jobs.*.steps[].CKV_GHA_3[18:22]',
            'jobs.*.steps[].CKV_GHA_3[18:22]',
            'jobs.job_name.CKV_GHA_3[18:22]']

    for key in keys:
        start_line, end_line = Runner.get_start_and_end_lines(key)
        assert start_line == '18'
        assert end_line == '22'


@pytest.mark.parametrize(
    "start_line,end_line,expected_job_name",
    [
        (10, 15, "container-test-job"),
        (8, 20, "container-test-job"),
        (24, 30, "second_job"),
        (25, 27, "second_job"),
        (5, 40, "")
    ],
)
def test_resolve_job_name(start_line, end_line, expected_job_name, definition):
    job_name = Runner.resolve_job_name(definition, start_line, end_line)

    assert job_name == expected_job_name


def test_modify_gha_keys_in_results(results, definition):
    Runner.modify_gha_keys_in_results(results, definition)

    assert list(results.keys()) == ['jobs.container-test-job', 'jobs.container-test-job.steps']
