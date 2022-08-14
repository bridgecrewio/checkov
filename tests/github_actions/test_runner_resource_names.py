import pytest
from checkov.github_actions.runner import Runner


def test_get_start_and_end_lines():
    keys = ['jobs.*.steps[].jobs.*.steps[].CKV_GHA_3[18:22]',
            'jobs.*.steps[].CKV_GHA_3[18:22]',
            'jobs.job_name.CKV_GHA_3[18:22]']

    for key in keys:
        start_line, end_line = Runner.get_start_and_end_lines(key)
        assert start_line == 18
        assert end_line == 22


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


@pytest.mark.parametrize(
    "key,expected_key",
    [
        ('jobs.container-test-job.CKV_GHA_3[7:23]', "jobs.container-test-job"),
        ('jobs.*.steps[].jobs.*.steps[].CKV_GHA_3[18:23]', "jobs.container-test-job.steps.Check for dockerenv file"),
    ],
)
def test_get_resource(key, expected_key, definition):
    runner = Runner()

    new_key = runner.get_resource("", key, [], definition)

    assert new_key == expected_key


@pytest.mark.parametrize(
    "start_line,end_line,expected_key",
    [
        (9, 17, "jobs.container-test-job"),
        (24, 30, "jobs.second_job"),
        (35, 40, "")
    ],
)
def test_generate_resource_key(start_line, end_line, expected_key, definition):
    runner = Runner()

    key = runner.generate_resource_key(definition, start_line, end_line)

    assert key == expected_key


@pytest.mark.parametrize(
    "start_line,end_line,old_key_format,expected_key",
    [
        (9, 17, 'jobs.container-test-job.CKV_GHA_3[7:23]', "jobs.container-test-job"),
        (24, 30, "jobs.second_job.CKV_GHA_3[24:30]", "jobs.second_job")
    ],
)
def test_generate_resource_key_generates_same_key_as_get_resource(start_line, end_line, old_key_format, expected_key, definition):
    runner = Runner()

    key1 = runner.get_resource("", old_key_format, [], definition)
    key2 = runner.generate_resource_key(definition, start_line, end_line)

    assert key1 == key2 == expected_key

