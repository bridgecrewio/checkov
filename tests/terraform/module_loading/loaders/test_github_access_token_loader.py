from unittest.mock import patch

import pytest

from checkov.terraform.module_loading.loaders.github_access_token_loader import (
    GithubAccessTokenLoader,
    _extract_github_org,
)
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


class TestExtractGithubOrg:
    """Tests for _extract_github_org helper."""

    @pytest.mark.parametrize("source, expected_org", [
        ("github.com/my-org/my-repo", "my-org"),
        ("git::https://github.com/my-org/my-repo.git", "my-org"),
        ("git@github.com:my-org/my-repo.git", "my-org"),
        ("git::ssh://git@github.com/my-org/my-repo.git", "my-org"),
        ("https://github.com/my-org/my-repo", "my-org"),
        ("github.com/my-org/my-repo//subdir?ref=v1.0", "my-org"),
    ])
    def test_extract_org_from_various_formats(self, source: str, expected_org: str) -> None:
        assert _extract_github_org(source) == expected_org

    def test_extract_org_returns_none_for_non_github(self) -> None:
        assert _extract_github_org("gitlab.com/org/repo") is None

    def test_extract_org_returns_none_for_empty(self) -> None:
        assert _extract_github_org("") is None


class TestGithubCredentialScoping:
    """Tests for GITHUB_PAT credential scoping in _is_matching_loader."""

    def _make_loader_and_params(self, source: str) -> tuple[GithubAccessTokenLoader, ModuleParams]:
        loader = GithubAccessTokenLoader()
        module_params = _make_module_params(source)
        loader.discover(module_params)
        return loader, module_params

    @patch.dict("os.environ", {"GITHUB_PAT": "ghp_test123"}, clear=False)
    def test_github_pat_not_injected_when_no_allowed_orgs(self) -> None:
        """When GITHUB_PAT is set but GITHUB_PAT_ALLOWED_ORGS is not configured,
        credentials should not be injected (safe default)."""
        loader, module_params = self._make_loader_and_params("github.com/some-org/some-repo")
        # Ensure GITHUB_PAT_ALLOWED_ORGS is not set
        with patch.dict("os.environ", {}, clear=False):
            env = dict(**__import__("os").environ)
            env.pop("GITHUB_PAT_ALLOWED_ORGS", None)
            with patch.dict("os.environ", env, clear=True):
                # Re-discover to pick up the PAT
                loader.discover(module_params)
                result = loader._is_matching_loader(module_params)

        assert result is False
        assert "ghp_test123" not in module_params.module_source

    @patch.dict("os.environ", {"GITHUB_PAT": "ghp_test123", "GITHUB_PAT_ALLOWED_ORGS": "my-org"}, clear=False)
    def test_github_pat_injected_when_org_matches(self) -> None:
        """When GITHUB_PAT is set and the org matches GITHUB_PAT_ALLOWED_ORGS,
        credentials should be injected."""
        loader, module_params = self._make_loader_and_params("github.com/my-org/my-repo")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "ghp_test123" in module_params.module_source
        assert "x-access-token:ghp_test123@github.com/my-org/my-repo" in module_params.module_source

    @patch.dict("os.environ", {"GITHUB_PAT": "ghp_test123", "GITHUB_PAT_ALLOWED_ORGS": "my-org"}, clear=False)
    def test_github_pat_not_injected_when_org_does_not_match(self) -> None:
        """When GITHUB_PAT is set but the org does not match GITHUB_PAT_ALLOWED_ORGS,
        credentials should not be injected."""
        loader, module_params = self._make_loader_and_params("github.com/other-org/some-repo")
        result = loader._is_matching_loader(module_params)

        assert result is False
        assert "ghp_test123" not in module_params.module_source

    @patch.dict("os.environ", {"GITHUB_PAT": "ghp_test123", "GITHUB_PAT_ALLOWED_ORGS": "*"}, clear=False)
    def test_github_pat_wildcard_allows_all(self) -> None:
        """When GITHUB_PAT_ALLOWED_ORGS is set to '*', credentials should be
        injected for any GitHub org."""
        loader, module_params = self._make_loader_and_params("github.com/any-org/any-repo")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "ghp_test123" in module_params.module_source

    @patch.dict("os.environ", {"GITHUB_PAT": "ghp_test123", "GITHUB_PAT_ALLOWED_ORGS": "org-a, org-b, org-c"}, clear=False)
    def test_github_pat_multiple_allowed_orgs(self) -> None:
        """Multiple orgs in GITHUB_PAT_ALLOWED_ORGS should all be accepted."""
        loader, module_params = self._make_loader_and_params("github.com/org-b/some-repo")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "ghp_test123" in module_params.module_source

    @patch.dict("os.environ", {"GITHUB_PAT": "ghp_test123", "GITHUB_PAT_ALLOWED_ORGS": "My-Org"}, clear=False)
    def test_github_pat_case_insensitive_org_match(self) -> None:
        """Org matching should be case-insensitive."""
        loader, module_params = self._make_loader_and_params("github.com/my-org/some-repo")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "ghp_test123" in module_params.module_source

    @patch.dict("os.environ", {"GITHUB_PAT": "ghp_test123", "GITHUB_PAT_ALLOWED_ORGS": "my-org"}, clear=False)
    def test_github_pat_injected_for_git_ssh_format(self) -> None:
        """Credentials should be injected for git@github.com:org/repo format."""
        loader, module_params = self._make_loader_and_params("git@github.com:my-org/my-repo.git")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "ghp_test123" in module_params.module_source

    @patch.dict("os.environ", {"GITHUB_PAT": "ghp_test123", "GITHUB_PAT_ALLOWED_ORGS": "my-org"}, clear=False)
    def test_github_pat_injected_for_git_https_format(self) -> None:
        """Credentials should be injected for git::https://github.com/org/repo format."""
        loader, module_params = self._make_loader_and_params("git::https://github.com/my-org/my-repo.git")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "ghp_test123" in module_params.module_source

    @patch.dict("os.environ", {"GITHUB_PAT": "ghp_test123", "GITHUB_PAT_ALLOWED_ORGS": "my-org"}, clear=False)
    def test_github_pat_injected_for_git_ssh_protocol_format(self) -> None:
        """Credentials should be injected for git::ssh://git@github.com/org/repo format."""
        loader, module_params = self._make_loader_and_params("git::ssh://git@github.com/my-org/my-repo.git")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "ghp_test123" in module_params.module_source

    def test_github_no_pat_returns_false(self) -> None:
        """When GITHUB_PAT is not set, _is_matching_loader should return False."""
        loader = GithubAccessTokenLoader()
        module_params = _make_module_params("github.com/my-org/my-repo")
        loader.discover(module_params)
        # Ensure token is empty (no PAT set)
        module_params.token = ""
        result = loader._is_matching_loader(module_params)

        assert result is False
