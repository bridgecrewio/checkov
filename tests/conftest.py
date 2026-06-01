from copy import copy, deepcopy
from checkov.common.checks.base_check_registry import BaseCheckRegistry
import pytest


# ──────────────────────────────────────────────────────────────────────────────
# DIAGNOSTIC: progress logging + SIGSEGV faulthandler.
#
# Each line has the format:
#   <iso-ts>  pid=<pid>  <SETUP|BODY|TEARDOWN|FINISHED>  <nodeid>
#
# - iso-ts maps to the action-log timestamp when a crash/cancel happens.
# - pid distinguishes original worker (that crashed) from xdist-spawned
#   replacement worker (different pids, same /tmp file).
# - SETUP / BODY / TEARDOWN / FINISHED isolate WHERE the hang occurs:
#     SETUP   = pytest_runtest_setup hook fired (fixtures running)
#     BODY    = pytest_runtest_call hook fired (test function executing)
#     TEARDOWN = pytest_runtest_teardown fired (autouse fixture cleanup)
#     FINISHED = full test+teardown cycle returned cleanly
#   If we see SETUP/BODY/TEARDOWN without FINISHED → that phase hung.
#
# faulthandler.register(SIGSEGV) writes the Python+C stack to a separate
# .faulthandler.log file when a real segfault hits. Empty file = HANG.
import os as _diag_os
import datetime as _diag_dt
import faulthandler as _diag_faulthandler
import signal as _diag_signal

_DIAG_WORKER_ID = _diag_os.environ.get("PYTEST_XDIST_WORKER", "master")
_DIAG_PROGRESS_PATH = f"/tmp/pytest-worker-{_DIAG_WORKER_ID}.log"
_DIAG_FAULT_PATH = f"/tmp/pytest-worker-{_DIAG_WORKER_ID}.faulthandler.log"
_DIAG_PID = _diag_os.getpid()

try:
    _diag_fault_fh = open(_DIAG_FAULT_PATH, "a", buffering=1, encoding="utf-8")
    _diag_fault_fh.write(
        f"# faulthandler armed at {_diag_dt.datetime.now(_diag_dt.timezone.utc).isoformat()} "
        f"pid={_DIAG_PID} worker={_DIAG_WORKER_ID}\n"
    )
    _diag_fault_fh.flush()
    _diag_faulthandler.enable(file=_diag_fault_fh, all_threads=True)
    _diag_faulthandler.register(
        _diag_signal.SIGTERM, file=_diag_fault_fh, all_threads=True, chain=True,
    )
except Exception:
    _diag_fault_fh = None  # Best-effort.


def _diag_write(kind: str, nodeid: str) -> None:
    try:
        ts = _diag_dt.datetime.now(_diag_dt.timezone.utc).isoformat(timespec="milliseconds")
        line = f"{ts}\tpid={_DIAG_PID}\t{kind}\t{nodeid}\n"
        with open(_DIAG_PROGRESS_PATH, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            _diag_os.fsync(f.fileno())
    except Exception:
        pass


def pytest_runtest_setup(item) -> None:
    _diag_write("SETUP", item.nodeid)


def pytest_runtest_call(item) -> None:
    _diag_write("BODY", item.nodeid)


def pytest_runtest_teardown(item, nextitem) -> None:
    _diag_write("TEARDOWN", item.nodeid)


def pytest_runtest_logfinish(nodeid: str, location: tuple) -> None:
    _diag_write("FINISHED", nodeid)
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