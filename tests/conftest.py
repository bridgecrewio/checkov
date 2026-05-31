from copy import copy, deepcopy
from checkov.common.checks.base_check_registry import BaseCheckRegistry
import pytest


# ──────────────────────────────────────────────────────────────────────────────
# DIAGNOSTIC: log every test start to a per-worker file, so the LAST line
# before a SIGSEGV tells us which test was running when the crash happened.
#
# Why a file (and not stderr):
#   (a) xdist captures stderr from worker subprocesses and discards it from
#       the controller output unless `-s` is also passed, so stderr-based
#       breadcrumbs are invisible in CI logs.
#   (b) Writing to a file with explicit fsync survives a worker segfault
#       because fsync'd data is durable across abnormal process termination
#       (POSIX guarantee).
#
# Each worker gets its own file via the PYTEST_XDIST_WORKER env var set by
# xdist (e.g. `gw0`, `gw1`). The CI workflow has a `failure()` step that
# tails these files so the trigger test appears in the action log.
import os as _diag_os

_DIAG_WORKER_ID = _diag_os.environ.get("PYTEST_XDIST_WORKER", "master")
_DIAG_PROGRESS_PATH = f"/tmp/pytest-worker-{_DIAG_WORKER_ID}.log"


def pytest_runtest_logstart(nodeid: str, location: tuple) -> None:
    """Append the about-to-run nodeid to /tmp/pytest-worker-<id>.log with
    fsync, so the file's last line identifies the crashing test even if
    the worker dies inside the test body."""
    try:
        with open(_DIAG_PROGRESS_PATH, "a", encoding="utf-8") as f:
            f.write(f"{nodeid}\n")
            f.flush()
            _diag_os.fsync(f.fileno())
    except Exception:
        # Best-effort only — never break the test run because of diag.
        pass
# ──────────────────────────────────────────────────────────────────────────────


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
