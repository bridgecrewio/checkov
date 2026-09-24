import pytest

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader
from checkov.terraform.module_loading.module_params import ModuleParams


def _make_module_params(source: str) -> ModuleParams:
    """Helper to create a ModuleParams instance with default test values."""
    return ModuleParams(
        root_dir="test",
        current_dir="test",
        source=source,
        source_version="latest",
        dest_dir="test",
        external_modules_folder_name="test",
        inner_module="",
        tf_managed=False,
    )


@pytest.mark.parametrize("source, expected_root_module, expected_inner_module", [
    ("git::git@github.com:test-inner-module/out-module//inner-module?ref=main",
     "github.com:test-inner-module/out-module", "inner-module"),
    ("git::https://github.com:test-inner-module/out-module//inner-module?ref=main",
     "github.com:test-inner-module/out-module", "inner-module"),
    ("git::https://github.com:test-only-outer-module/out-module",
     "github.com:test-only-outer-module/out-module", ""),
    ("git::ssh://github.com:test-only-outer-module/out-module",
     "github.com:test-only-outer-module/out-module", ""),
    ("https://github.com:test-only-outer-module/out-module",
     "github.com:test-only-outer-module/out-module", ""),
    ("https://github.com:test-with-inner-module-no-git-prefix/out-module//in-module",
     "github.com:test-with-inner-module-no-git-prefix/out-module", "in-module")
]
                         )
def test__parse_module_source(source: str, expected_root_module: str, expected_inner_module: str) -> None:
    git_loader = GenericGitLoader()
    module_params = ModuleParams(
        root_dir="test",
        current_dir="test",
        source=source,
        source_version="source_version",
        dest_dir="test",
        external_modules_folder_name="test",
        inner_module="",
        tf_managed=False
    )
    module_source = git_loader._parse_module_source(module_params)
    assert module_source.root_module == expected_root_module
    assert module_source.inner_module == expected_inner_module


class TestCredentialScoping:
    """Tests for VCS_TOKEN credential scoping in _is_matching_loader."""

    def test_credentials_not_injected_when_vcs_base_url_not_set(self) -> None:
        """When VCS_BASE_URL is not set, credentials should not be injected
        into the module source URL even if VCS_TOKEN and VCS_USERNAME are available."""
        git_loader = GenericGitLoader()
        module_params = _make_module_params("git::https://some-server.example.com/org/repo")
        module_params.token = "test-token"
        module_params.username = "test-user"
        module_params.vcs_base_url = ""
        module_params.module_source_prefix = None

        result = git_loader._is_matching_loader(module_params)

        assert result is True
        assert "test-token" not in module_params.module_source
        assert "test-user" not in module_params.module_source
        assert module_params.module_source == "git::https://some-server.example.com/org/repo"

    def test_credentials_injected_when_vcs_base_url_matches(self) -> None:
        """When VCS_BASE_URL is set and the module source matches it,
        credentials should be injected into the module source URL."""
        git_loader = GenericGitLoader()
        module_params = _make_module_params("git::https://gitlab.example.com/org/repo")
        module_params.token = "test-token"
        module_params.username = "test-user"
        module_params.vcs_base_url = "https://gitlab.example.com"
        module_params.module_source_prefix = "git::https://gitlab.example.com"

        result = git_loader._is_matching_loader(module_params)

        assert result is True
        assert "test-user:test-token@" in module_params.module_source
        assert module_params.module_source == "git::https://test-user:test-token@gitlab.example.com/org/repo"

    def test_credentials_not_injected_when_vcs_base_url_does_not_match(self) -> None:
        """When VCS_BASE_URL is set but the module source points to a different server,
        credentials should not be injected."""
        git_loader = GenericGitLoader()
        module_params = _make_module_params("git::https://other-server.example.com/org/repo")
        module_params.token = "test-token"
        module_params.username = "test-user"
        module_params.vcs_base_url = "https://gitlab.example.com"
        module_params.module_source_prefix = "git::https://gitlab.example.com"

        result = git_loader._is_matching_loader(module_params)

        # The source doesn't start with the VCS_BASE_URL prefix, so it falls through
        # to the generic git:: check. Credentials should NOT be in the URL.
        assert result is True  # still matches generic git::https://
        assert "test-token" not in module_params.module_source
        assert "test-user" not in module_params.module_source
