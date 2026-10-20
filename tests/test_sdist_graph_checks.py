"""Regression test for https://github.com/bridgecrewio/checkov/issues/7724.

The published sdist contained no graph-check definition files (neither the
.yaml sources nor the generated .json), so any install built from the sdist
(pip --no-binary, distro/package-manager builds, Homebrew, air-gapped
mirrors) silently ran zero graph checks and reported misleadingly clean
results.

The YAML sources must be listed in the sdist manifest (MANIFEST.in) so that
setup.py's PreBuildCommand can transform them to JSON during build_py when
the install builds its wheel from the sdist.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _sdist_sources() -> set[str]:
    """Return the file list setuptools would put in the sdist.

    egg_info generates SOURCES.txt from MANIFEST.in without building
    anything, which is exactly the mechanism the sdist file list is drawn
    from.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        subprocess.run(
            [sys.executable, "setup.py", "-q", "egg_info", "--egg-base", tmp_dir],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        sources_txt = Path(tmp_dir, "checkov.egg-info", "SOURCES.txt")
        return set(sources_txt.read_text().splitlines())


def test_sdist_includes_all_graph_check_yaml() -> None:
    expected = {
        str(path.relative_to(REPO_ROOT))
        for path in REPO_ROOT.glob("checkov/*/checks/graph_checks/**/*.yaml")
    }
    assert expected, "no graph check YAML definitions found on disk"

    sources = _sdist_sources()
    missing = sorted(expected - sources)
    assert not missing, (
        f"{len(missing)} graph check definition(s) missing from the sdist "
        f"(first 5: {missing[:5]}); installs built from the sdist would "
        "silently run zero graph checks"
    )
