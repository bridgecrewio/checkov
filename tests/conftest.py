from copy import copy, deepcopy
from checkov.common.checks.base_check_registry import BaseCheckRegistry
import pytest


# ──────────────────────────────────────────────────────────────────────────────
# DIAGNOSTIC: progress logging + SIGSEGV faulthandler.
#
# Each line has the format:
#     <iso-ts>  pid=<pid>  <STARTED|FINISHED>  <nodeid>
#
# Why every field matters for the Python 3.9 segfault investigation:
#   * iso-ts maps directly to the "Fatal Python error" timestamp in the
#     action log, so we can identify the last log entry before the crash.
#   * pid distinguishes the ORIGINAL worker (that segfaulted) from the
#     xdist-spawned REPLACEMENT worker that continued after the crash —
#     both write to the same per-worker file but have different pids.
#   * STARTED vs FINISHED tells us whether the crash happened DURING a
#     test body or BETWEEN tests (e.g. during fixture teardown, gc, or
#     module import for the next test).
#
# Plus faulthandler.register(SIGSEGV) — Python's stdlib stack-trace
# dumper. When a C-level SIGSEGV fires it writes the Python AND C-level
# stack to /tmp/pytest-worker-<id>.faulthandler.log BEFORE the process
# dies. That stack identifies the offending C extension directly.
#
# The CI workflow uploads /tmp/pytest-worker-*.log AND
# /tmp/pytest-worker-*.faulthandler.log as an artifact on every run.
import os as _diag_os
import datetime as _diag_dt
import faulthandler as _diag_faulthandler
import signal as _diag_signal

_DIAG_WORKER_ID = _diag_os.environ.get("PYTEST_XDIST_WORKER", "master")
_DIAG_PROGRESS_PATH = f"/tmp/pytest-worker-{_DIAG_WORKER_ID}.log"
_DIAG_FAULT_PATH = f"/tmp/pytest-worker-{_DIAG_WORKER_ID}.faulthandler.log"
_DIAG_PID = _diag_os.getpid()

# Open the faulthandler sink and register it for SIGSEGV. The file handle
# must stay open for the life of the worker; faulthandler writes via the
# fd at signal-handler time (no Python heap allocations after the crash).
try:
    _diag_fault_fh = open(_DIAG_FAULT_PATH, "a", buffering=1, encoding="utf-8")
    _diag_fault_fh.write(
        f"# faulthandler armed at {_diag_dt.datetime.now(_diag_dt.timezone.utc).isoformat()} "
        f"pid={_DIAG_PID} worker={_DIAG_WORKER_ID}\n"
    )
    _diag_fault_fh.flush()
    _diag_faulthandler.enable(file=_diag_fault_fh, all_threads=True)
    # Also dump on SIGTERM (xdist sends this on worker shutdown) so we
    # can see a stack if the runner kills us due to the job timeout.
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
        # Best-effort only — never break the test run because of diag.
        pass


def pytest_runtest_logstart(nodeid: str, location: tuple) -> None:
    _diag_write("STARTED", nodeid)


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
