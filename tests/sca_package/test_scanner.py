import json
from pathlib import Path

import pytest
from mock import AsyncMock, MagicMock
from pytest_mock import MockerFixture

from checkov.sca_package.scanner import Scanner


def test_setup_twistcli_exists(mocker: MockerFixture, tmp_path: Path):
    # given
    scanner = Scanner()

    integration_mock = MagicMock()
    mocker.patch(
        "checkov.common.bridgecrew.vulnerability_scanning.integrations.package_scanning.package_scanning_integration.download_twistcli",
        side_effect=integration_mock,
    )

    # prepare local paths
    twistcli_path = tmp_path / "twistcli"
    twistcli_path.touch()
    scanner.twistcli_path = twistcli_path

    # when
    scanner.setup_twictcli()

    # then
    assert twistcli_path.exists()
    integration_mock.assert_not_called()


def test_setup_twistcli_not_exists(mocker: MockerFixture, tmp_path: Path):
    # given
    scanner = Scanner()

    def download_twistcli(cli_file_name: Path):
        cli_file_name.touch()

    integration_mock = MagicMock()
    integration_mock.side_effect = download_twistcli
    mocker.patch(
        "checkov.common.bridgecrew.vulnerability_scanning.integrations.package_scanning.package_scanning_integration.download_twistcli",
        side_effect=integration_mock,
    )

    # prepare local paths
    twistcli_path = tmp_path / "twistcli"
    scanner.twistcli_path = twistcli_path

    # when
    scanner.setup_twictcli()

    # then
    assert twistcli_path.exists()
    integration_mock.assert_called_once_with(twistcli_path)


def test_cleanup_twistcli_exists(tmp_path: Path):
    # given
    scanner = Scanner()

    # prepare local paths
    twistcli_path = tmp_path / "twistcli"
    twistcli_path.touch()
    scanner.twistcli_path = twistcli_path

    # when
    scanner.cleanup_twictcli()

    # then
    assert not twistcli_path.exists()


def test_cleanup_twistcli_not_exists(tmp_path: Path):
    # given
    scanner = Scanner()

    # prepare local paths
    twistcli_path = tmp_path / "twistcli"
    scanner.twistcli_path = twistcli_path

    # when
    scanner.cleanup_twictcli()

    # then
    assert not twistcli_path.exists()


@pytest.mark.asyncio
async def test_run_scan(mocker: MockerFixture, tmp_path: Path, mock_bc_integration, scan_result):
    # given
    subprocess_async_mock = AsyncMock()
    subprocess_async_mock.return_value.communicate = AsyncMock(return_value=("test".encode(encoding="utf-8"),
                                                                             "test".encode(encoding="utf-8")))
    subprocess_async_mock.return_value.wait = AsyncMock(return_value=0)
    mocker.patch("asyncio.create_subprocess_shell", side_effect=subprocess_async_mock)

    # prepare local paths
    app_temp_dir = tmp_path / "app"
    app_temp_dir.mkdir()
    output_path = app_temp_dir / "requirements_result.json"
    output_path.write_text(json.dumps(scan_result))

    # when
    result = await Scanner().run_scan(
        command="./twistcli coderepo scan",
        input_path=app_temp_dir / "requirements.txt",
        output_path=output_path,
    )

    # then
    assert result == scan_result
    assert not output_path.exists()
    subprocess_async_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_scan_fail_on_scan(mocker: MockerFixture, mock_bc_integration):
    # given
    subprocess_async_mock = AsyncMock()
    subprocess_async_mock.return_value.communicate = AsyncMock(return_value=("test".encode(encoding="utf-8"),
                                                                             "test".encode(encoding="utf-8")))
    subprocess_async_mock.return_value.wait = AsyncMock(return_value=1)
    mocker.patch("asyncio.create_subprocess_shell", side_effect=subprocess_async_mock)

    # when
    result = await Scanner().run_scan(
        command="./twistcli coderepo scan",
        input_path=Path("app/requirements.txt"),
        output_path=Path("app/requirements_result.json"),
    )

    # then
    assert result == {}
    subprocess_async_mock.assert_awaited_once()
