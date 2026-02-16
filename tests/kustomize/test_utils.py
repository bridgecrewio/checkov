from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from checkov.kustomize.utils import get_kustomize_version, get_kubectl_version


def test_get_kubectl_version_v1_27(mocker: MockerFixture):
    # given
    subprocess_mock = MagicMock()
    subprocess_mock.stdout = b'Client Version: version.Info{Major:"1", Minor:"27", GitVersion:"v1.27.2", GitCommit:"7f6f68fdabc4df88cfea2dcf9a19b2b830f1e647", GitTreeState:"clean", BuildDate:"2023-05-17T14:20:07Z", GoVersion:"go1.20.4", Compiler:"gc", Platform:"darwin/amd64"}\nKustomize Version: v5.0.1\n'

    mocker.patch("checkov.kustomize.utils.subprocess.run", return_value=subprocess_mock)

    # when
    version = get_kubectl_version(kubectl_command="kubectl")

    # then
    assert version == 1.27


def test_get_kubectl_version_v1_28(mocker: MockerFixture):
    # given
    subprocess_mock = MagicMock()
    subprocess_mock.stdout = b"Client Version: v1.28.0\nKustomize Version: v5.0.4-0.20230601165947-6ce0bf390ce3\n"

    mocker.patch("checkov.kustomize.utils.subprocess.run", return_value=subprocess_mock)

    # when
    version = get_kubectl_version(kubectl_command="kubectl")

    # then
    assert version == 1.28


def test_get_kubectl_version_none(mocker: MockerFixture):
    # given
    subprocess_mock = MagicMock()
    subprocess_mock.stdout = b"command not found: kubectl\n"

    mocker.patch("checkov.kustomize.utils.subprocess.run", return_value=subprocess_mock)

    # when
    version = get_kubectl_version(kubectl_command="kubectl")

    # then
    assert version is None


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
