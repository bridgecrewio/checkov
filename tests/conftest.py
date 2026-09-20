
import inspect
from copy import copy, deepcopy
from checkov.common.checks.base_check_registry import BaseCheckRegistry
import pytest

# aiohttp 3.14 added a required keyword-only 'stream_writer' argument to
# ClientResponse.__init__. aioresponses (<=0.7.9) builds ClientResponse
# instances directly and does not pass it, so its fabricated responses fail to
# construct. Supply a default here so the mocking library keeps working across
# both aiohttp 3.13 and 3.14. Can be dropped once aioresponses supports 3.14.
try:
    from aiohttp.client_reqrep import ClientResponse as _ClientResponse

    if "stream_writer" in inspect.signature(_ClientResponse.__init__).parameters:

        class _StubStreamWriter:
            """Minimal stand-in: ClientResponse only reads ``output_size``."""

            output_size = 0

        _original_client_response_init = _ClientResponse.__init__

        def _client_response_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            if kwargs.get("stream_writer") is None:
                kwargs["stream_writer"] = _StubStreamWriter()
            _original_client_response_init(self, *args, **kwargs)

        _ClientResponse.__init__ = _client_response_init  # type: ignore[method-assign]
except ImportError:  # pragma: no cover - aiohttp always present in test env
    pass

@pytest.fixture(scope='module', autouse=True)
def clean_bc_integration() -> None:
    from checkov.common.bridgecrew.platform_integration import bc_integration
    bc_integration.clean()


@pytest.fixture(scope='module', autouse=True)
def clean_feature_registry():
    from checkov.common.bridgecrew.integration_features.integration_feature_registry import integration_feature_registry
    old_features = copy(integration_feature_registry.features)
    before_registered_checks = copy(BaseCheckRegistry._BaseCheckRegistry__all_registered_checks)
    yield
    integration_feature_registry.features = old_features
    BaseCheckRegistry._BaseCheckRegistry__all_registered_checks = before_registered_checks




@pytest.fixture(scope='module', autouse=True)
def reset_checks():
    from checkov.terraform.checks.resource.registry import resource_registry as registry
    before_checks = deepcopy(registry.checks)
    before_wildcards_checks = deepcopy(registry.wildcard_checks)
    yield
    registry.checks = deepcopy(before_checks)
    registry.wildcard_checks = deepcopy(before_wildcards_checks)