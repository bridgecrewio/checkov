import os

from checkov.common.util.contextmanagers import temp_environ


def test_temp_environ():
    # given
    assert os.getenv("EXAMPLE_ENV_VAR") is None

    # when/then
    with temp_environ(EXAMPLE_ENV_VAR="example"):
        assert os.getenv("EXAMPLE_ENV_VAR") == "example"

    assert os.getenv("EXAMPLE_ENV_VAR") is None


def test_temp_environ_existing_env():
    # given
    os.environ["EXAMPLE_ENV_VAR"] = "example"

    # when/then
    with temp_environ(EXAMPLE_ENV_VAR="override_example"):
        assert os.getenv("EXAMPLE_ENV_VAR") == "override_example"

    assert os.environ["EXAMPLE_ENV_VAR"] == "example"
    del os.environ["EXAMPLE_ENV_VAR"]  # cleanup
