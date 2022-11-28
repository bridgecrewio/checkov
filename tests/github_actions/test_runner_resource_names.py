import pytest
from checkov.github_actions.runner import Runner


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
    job_name = Runner.resolve_sub_name(definition, start_line, end_line, tag='jobs')

    assert job_name == expected_job_name


@pytest.mark.parametrize(
    "key,expected_key, supported_entities, start_line, end_line",
    [
        ('jobs.container-test-job.CKV_GHA_3[7:23]', "jobs(container-test-job)",
         ('jobs', 'jobs.*.steps[]'), 7, 23),
        ('jobs.*.steps[].jobs.*.steps[].CKV_GHA_3[18:23]', "jobs(container-test-job).steps[1](Check for dockerenv file)",
         ('jobs', 'jobs.*.steps[]'), 18, 23),
        ('jobs.*.steps[].jobs.*.steps[].CKV_GHA_3[31:35]', "jobs(no_step_name_job).steps[1]",
        ('jobs', 'jobs.*.steps[]'), 31, 35),
    ],
)
def test_get_resource(key, supported_entities, expected_key, start_line, end_line, definition):
    runner = Runner()
    file_path = "mock_path"
    runner.definitions[file_path] = definition

    new_key = runner.get_resource(file_path, key, supported_entities, start_line, end_line)

    assert new_key == expected_key
