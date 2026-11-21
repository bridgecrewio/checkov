"""The ``ecdsa`` dependency is optional: default installs must stay clean.

Signature verification is opt-in behind ``--external-checks-public-key``, so
``ecdsa`` lives in the ``signed-checks`` extra. These tests pin the three
properties that keep a default install free of CVE-2024-23342:

1. importing the verification package (and ``checkov`` itself) never imports
   ``ecdsa``;
2. asking for a key without the extra raises the actionable
   ``SignatureVerificationError`` instead of a bare ``ModuleNotFoundError``;
3. ``setup.py`` declares the dependency only as the ``signed-checks`` extra.

The "without the extra" cases run in a subprocess whose ``sys.path`` hides
``ecdsa`` — the test environment installs it (the suite signs its own
fixtures), so an in-process check could not tell the two states apart.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from checkov.common.external_checks.verification import _ecdsa
from checkov.common.external_checks.verification.errors import (
    SignatureVerificationError,
)


REPO_ROOT = Path(__file__).resolve().parents[4]

# Runs in the repo root with ``ecdsa`` blocked from import.
_BLOCKER = """
import sys

class _BlockEcdsa:
    def find_module(self, name, path=None):
        return self.find_spec(name, path)

    def find_spec(self, name, path=None, target=None):
        if name == "ecdsa" or name.startswith("ecdsa."):
            raise ModuleNotFoundError(f"blocked by test: {name}")
        return None

sys.meta_path.insert(0, _BlockEcdsa())
for _name in [m for m in list(sys.modules) if m == "ecdsa" or m.startswith("ecdsa.")]:
    del sys.modules[_name]
"""


def _run_without_ecdsa(body: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        [sys.executable, "-c", _BLOCKER + body],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


# --------------------------------------------------------------------------
# 1. Importing the package does not drag the optional dependency in.
# --------------------------------------------------------------------------


def test_verification_package_import_does_not_import_ecdsa():
    """A plain import must leave ``ecdsa`` out of ``sys.modules``."""
    code = (
        "import sys\n"
        "import checkov.common.external_checks.verification\n"
        "leaked = [m for m in sys.modules if m == 'ecdsa' or m.startswith('ecdsa.')]\n"
        "assert not leaked, leaked\n"
    )
    result = _run_without_ecdsa(code)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "entry_point",
    [
        "checkov.common.external_checks.verification.keys",
        "checkov.common.external_checks.verification.verifier",
        "checkov.common.external_checks.verification.sources_registry",
        "checkov.common.checks.base_check_registry",
    ],
)
def test_verification_entry_points_load_without_ecdsa(entry_point: str):
    """Every module on the scan path must import without the extra installed."""
    code = f"import {entry_point}\n"
    result = _run_without_ecdsa(code)
    assert result.returncode == 0, result.stderr


def test_checkov_main_imports_without_ecdsa():
    """The CLI module is what every ``checkov`` run loads first."""
    code = "import checkov.main\n"
    result = _run_without_ecdsa(code)
    assert result.returncode == 0, result.stderr


# --------------------------------------------------------------------------
# 2. Missing extra surfaces as the verification error, not ModuleNotFoundError.
# --------------------------------------------------------------------------


def test_load_public_keys_without_ecdsa_reports_missing_extra(tmp_path: Path):
    """The failure must name the extra and carry the verification error type."""
    pem = tmp_path / "pub.pem"
    pem.write_text("-----BEGIN PUBLIC KEY-----\nAAAA\n-----END PUBLIC KEY-----\n")
    code = (
        "import sys\n"
        "from checkov.common.external_checks.verification import (\n"
        "    SignatureVerificationError,\n"
        "    load_public_keys,\n"
        ")\n"
        f"try:\n"
        f"    load_public_keys([{str(pem)!r}])\n"
        "except SignatureVerificationError as exc:\n"
        "    msg = str(exc)\n"
        "    assert 'signed-checks' in msg, msg\n"
        "    assert 'ecdsa' in msg, msg\n"
        "else:\n"
        "    raise AssertionError('load_public_keys did not raise')\n"
    )
    result = _run_without_ecdsa(code)
    assert result.returncode == 0, result.stderr


def test_is_available_reflects_installed_extra():
    """``is_available`` is the non-raising probe callers can branch on."""
    assert _ecdsa.is_available() is True  # the test environment installs ecdsa


def test_is_available_returns_false_without_ecdsa():
    code = (
        "from checkov.common.external_checks.verification import _ecdsa\n"
        "assert _ecdsa.is_available() is False\n"
    )
    result = _run_without_ecdsa(code)
    assert result.returncode == 0, result.stderr


# --------------------------------------------------------------------------
# 3. Packaging keeps ``ecdsa`` out of the default install.
# --------------------------------------------------------------------------


def _setup_py_metadata() -> "dict[str, object]":
    """Parse ``setup.py`` without executing it (it imports setuptools)."""
    import ast

    tree = ast.parse((REPO_ROOT / "setup.py").read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not getattr(node.func, "id", "") == "setup":
            continue
        metadata: "dict[str, object]" = {}
        for keyword in node.keywords:
            if keyword.arg in ("install_requires", "extras_require"):
                metadata[keyword.arg] = ast.literal_eval(keyword.value)
        return metadata
    raise AssertionError("setup() call not found in setup.py")


def test_ecdsa_is_only_declared_in_the_signed_checks_extra():
    """A default ``pip install checkov`` must not pull ecdsa in."""
    metadata = _setup_py_metadata()
    install_requires = metadata["install_requires"]
    extras_require = metadata["extras_require"]

    assert isinstance(install_requires, list)
    assert not [req for req in install_requires if req.startswith("ecdsa")], (
        "ecdsa must not be in install_requires; it belongs to the signed-checks extra"
    )

    assert isinstance(extras_require, dict)
    signed_checks = extras_require.get("signed-checks")
    assert signed_checks, "the signed-checks extra is missing from extras_require"
    assert [req for req in signed_checks if req.startswith("ecdsa")], (
        f"signed-checks extra must pin ecdsa, got {signed_checks}"
    )


def test_pipfile_keeps_ecdsa_out_of_default_packages():
    """pre-commit's pipenv-setup check requires the two files to agree."""
    import tomllib

    pipfile = tomllib.loads((REPO_ROOT / "Pipfile").read_text())
    packages = pipfile.get("packages") or {}
    dev_packages = pipfile.get("dev-packages") or {}

    assert "ecdsa" not in packages, (
        "Pipfile [packages] mirrors install_requires; ecdsa belongs in "
        "[dev-packages] so the test suite can sign its fixtures"
    )
    assert "ecdsa" in dev_packages
