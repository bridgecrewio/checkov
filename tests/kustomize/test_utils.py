from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from checkov.kustomize.utils import get_kustomize_version


def test_get_kustomize_version_v4(mocker: MockerFixture):
    # given
    subprocess_mock = MagicMock()
    subprocess_mock.stdout = b"{Version:kustomize/v4.5.7 GitCommit:56d82a8378dfc8dc3b3b1085e5a6e67b82966bd7 BuildDate:2022-08-02T16:28:01Z GoOs:darwin GoArch:amd64}\n"

    mocker.patch("checkov.kustomize.utils.subprocess.run", return_value=subprocess_mock)

    # when
    version = get_kustomize_version(kustomize_command="kustomize")

    # then
    assert version == "v4.5.7"


def test_get_kustomize_version_v5(mocker: MockerFixture):
    # given
    subprocess_mock = MagicMock()
    subprocess_mock.stdout = b"v5.0.0\n"

    mocker.patch("checkov.kustomize.utils.subprocess.run", return_value=subprocess_mock)

    # when
    version = get_kustomize_version(kustomize_command="kustomize")

    # then
    assert version == "v5.0.0"


def test_get_kustomize_version_none(mocker: MockerFixture):
    # given
    subprocess_mock = MagicMock()
    subprocess_mock.stdout = b"command not found: kustomize\n"

    mocker.patch("checkov.kustomize.utils.subprocess.run", return_value=subprocess_mock)

    # when
    version = get_kustomize_version(kustomize_command="kustomize")

    # then
    assert version is None
