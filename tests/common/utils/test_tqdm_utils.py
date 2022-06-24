import os

from pytest_mock import MockerFixture

from checkov.common.util.tqdm_utils import ProgressBar


def test_is_off_with_run_in_docker(mocker: MockerFixture):
    # given
    mocker.patch.dict(os.environ, {"RUN_IN_DOCKER": "True"})

    # when
    bar = ProgressBar("terraform")

    # then
    assert bar.is_off is True


def test_is_off_with_log_level(mocker: MockerFixture):
    # given
    mocker.patch.dict(os.environ, {"LOG_LEVEL": "INFO"})

    # when
    bar = ProgressBar("terraform")

    # then
    assert bar.is_off is True


def test_is_off_with_not_isatty(mocker: MockerFixture):
    # given
    mocker.patch("sys.__stdout__.isatty", return_value=False)

    # when
    bar = ProgressBar("terraform")

    # then
    assert bar.is_off is True
