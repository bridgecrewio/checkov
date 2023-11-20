import pytest
from pytest_mock import MockerFixture

from checkov.common.bridgecrew.platform_integration import BcPlatformIntegration
from checkov.common.cache.cache import file_cache


@pytest.fixture
def enable_cache():
    file_cache.enabled = True
    file_cache.init_cache()
    file_cache.clear_caches()

    yield

    file_cache.clear_caches()
    file_cache.enabled = False


def test_get_public_run_config_cache(mocker: MockerFixture, enable_cache):
    # given
    platform_integration = BcPlatformIntegration()
    spy = mocker.spy(platform_integration, "setup_http_manager")  # this is used inside '_get_public_run_config()'
    platform_integration.get_public_run_config()

    assert platform_integration.public_metadata_response is not None

    # when
    platform_integration.get_public_run_config()

    # then
    assert platform_integration.public_metadata_response is not None
    assert spy.call_count == 1
