
# ──────────────────────────────────────────────────────────────────────────────
# DIAGNOSTIC: disable pycares (via aiodns) in the test environment.
#
# The unit-tests(3.9) job segfaults inside pytest's tmp_path fixture during
# `posixpath.realpath`, with the pycares background shutdown thread parked
# on a SimpleQueue.get(). Hypothesis: pycares's C-extension thread races
# with realpath syscalls on Python 3.9 + ubuntu-latest runners.
#
# This block forces aiohttp to use its pure-Python `ThreadedResolver`
# (no pycares thread ever spawned), proving or disproving the hypothesis.
# If the segfault disappears on the next CI run, pycares is the culprit
# and this becomes the permanent fix. If it persists, pycares was a red
# herring and we revert this block.
#
# IMPORTANT: must run BEFORE any `import checkov...` because checkov's
# http_utils does `import aiohttp` at module level, which would already
# load pycares if aiodns is available.
import sys as _sys
import aiohttp as _aiohttp  # noqa: E402 — must come BEFORE checkov import
_sys.modules["aiodns"] = None  # type: ignore[assignment]
# `http_utils.py` calls `aiohttp.AsyncResolver()` which raises RuntimeError
# when aiodns is None, so we redirect the symbol to the pure-Python resolver.
_aiohttp.AsyncResolver = _aiohttp.ThreadedResolver  # type: ignore[misc]
del _sys, _aiohttp
# ──────────────────────────────────────────────────────────────────────────────

from copy import copy, deepcopy
from checkov.common.checks.base_check_registry import BaseCheckRegistry
import pytest

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