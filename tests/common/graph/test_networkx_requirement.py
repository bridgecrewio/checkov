import re
from pathlib import Path

import networkx
from packaging.specifiers import SpecifierSet
from packaging.version import Version

REPO_ROOT = Path(__file__).parents[3]


def _declared_networkx_specifier(file_name: str, pattern: str) -> SpecifierSet:
    content = (REPO_ROOT / file_name).read_text()
    match = re.search(pattern, content, re.MULTILINE)
    assert match, f"networkx requirement not found in {file_name}"
    return SpecifierSet(match.group(1))


def test_installed_networkx_satisfies_declared_requirement():
    # the declared requirement must not exclude the networkx release the test suite runs against
    setup_spec = _declared_networkx_specifier("setup.py", r'"networkx([^"]*)"')
    pipfile_spec = _declared_networkx_specifier("Pipfile", r'^networkx = "([^"]*)"')

    assert setup_spec == pipfile_spec
    assert Version(networkx.__version__) in setup_spec
