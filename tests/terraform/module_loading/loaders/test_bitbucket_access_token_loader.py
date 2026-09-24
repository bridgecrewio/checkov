from unittest.mock import patch

import pytest

from checkov.terraform.module_loading.loaders.bitbucket_access_token_loader import (
    BitbucketAccessTokenLoader,
    _extract_bitbucket_workspace,
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


class TestExtractBitbucketWorkspace:
    """Tests for _extract_bitbucket_workspace helper."""

    @pytest.mark.parametrize("source, expected_workspace", [
        ("bitbucket.org/my-workspace/my-repo", "my-workspace"),
        ("git::https://bitbucket.org/my-workspace/my-repo.git", "my-workspace"),
        ("git@bitbucket.org:my-workspace/my-repo.git", "my-workspace"),
        ("git::ssh://git@bitbucket.org/my-workspace/my-repo.git", "my-workspace"),
        ("https://bitbucket.org/my-workspace/my-repo", "my-workspace"),
        ("bitbucket.org/my-workspace/my-repo//subdir?ref=v1.0", "my-workspace"),
    ])
    def test_extract_workspace_from_various_formats(self, source: str, expected_workspace: str) -> None:
        assert _extract_bitbucket_workspace(source) == expected_workspace

    def test_extract_workspace_returns_none_for_non_bitbucket(self) -> None:
        assert _extract_bitbucket_workspace("github.com/org/repo") is None

    def test_extract_workspace_returns_none_for_empty(self) -> None:
        assert _extract_bitbucket_workspace("") is None


class TestBitbucketCredentialScoping:
    """Tests for BITBUCKET_TOKEN credential scoping in _is_matching_loader."""

    def _make_loader_and_params(self, source: str) -> tuple[BitbucketAccessTokenLoader, ModuleParams]:
        loader = BitbucketAccessTokenLoader()
        module_params = _make_module_params(source)
        loader.discover(module_params)
        return loader, module_params

    @patch.dict("os.environ", {"BITBUCKET_TOKEN": "bb_test123"}, clear=False)
    def test_bitbucket_token_not_injected_when_no_allowed_workspaces(self) -> None:
        """When BITBUCKET_TOKEN is set but BITBUCKET_ALLOWED_WORKSPACES is not configured,
        credentials should not be injected (safe default)."""
        loader, module_params = self._make_loader_and_params("bitbucket.org/some-ws/some-repo")
        # Ensure BITBUCKET_ALLOWED_WORKSPACES is not set
        with patch.dict("os.environ", {}, clear=False):
            env = dict(**__import__("os").environ)
            env.pop("BITBUCKET_ALLOWED_WORKSPACES", None)
            with patch.dict("os.environ", env, clear=True):
                loader.discover(module_params)
                result = loader._is_matching_loader(module_params)

        assert result is False
        assert "bb_test123" not in module_params.module_source

    @patch.dict("os.environ", {"BITBUCKET_TOKEN": "bb_test123", "BITBUCKET_ALLOWED_WORKSPACES": "my-ws"}, clear=False)
    def test_bitbucket_token_injected_when_workspace_matches(self) -> None:
        """When BITBUCKET_TOKEN is set and the workspace matches BITBUCKET_ALLOWED_WORKSPACES,
        credentials should be injected."""
        loader, module_params = self._make_loader_and_params("bitbucket.org/my-ws/my-repo")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "bb_test123" in module_params.module_source
        assert "x-token-auth:bb_test123@bitbucket.org/my-ws/my-repo" in module_params.module_source

    @patch.dict("os.environ", {"BITBUCKET_TOKEN": "bb_test123", "BITBUCKET_ALLOWED_WORKSPACES": "my-ws"}, clear=False)
    def test_bitbucket_token_not_injected_when_workspace_does_not_match(self) -> None:
        """When BITBUCKET_TOKEN is set but the workspace does not match BITBUCKET_ALLOWED_WORKSPACES,
        credentials should not be injected."""
        loader, module_params = self._make_loader_and_params("bitbucket.org/other-ws/some-repo")
        result = loader._is_matching_loader(module_params)

        assert result is False
        assert "bb_test123" not in module_params.module_source

    @patch.dict("os.environ", {"BITBUCKET_TOKEN": "bb_test123", "BITBUCKET_ALLOWED_WORKSPACES": "*"}, clear=False)
    def test_bitbucket_token_wildcard_allows_all(self) -> None:
        """When BITBUCKET_ALLOWED_WORKSPACES is set to '*', credentials should be
        injected for any Bitbucket workspace."""
        loader, module_params = self._make_loader_and_params("bitbucket.org/any-ws/any-repo")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "bb_test123" in module_params.module_source

    @patch.dict("os.environ", {"BITBUCKET_TOKEN": "bb_test123", "BITBUCKET_ALLOWED_WORKSPACES": "ws-a, ws-b, ws-c"}, clear=False)
    def test_bitbucket_token_multiple_allowed_workspaces(self) -> None:
        """Multiple workspaces in BITBUCKET_ALLOWED_WORKSPACES should all be accepted."""
        loader, module_params = self._make_loader_and_params("bitbucket.org/ws-b/some-repo")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "bb_test123" in module_params.module_source

    @patch.dict("os.environ", {"BITBUCKET_TOKEN": "bb_test123", "BITBUCKET_ALLOWED_WORKSPACES": "My-WS"}, clear=False)
    def test_bitbucket_token_case_insensitive_workspace_match(self) -> None:
        """Workspace matching should be case-insensitive."""
        loader, module_params = self._make_loader_and_params("bitbucket.org/my-ws/some-repo")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "bb_test123" in module_params.module_source

    @patch.dict("os.environ", {"BITBUCKET_TOKEN": "bb_test123", "BITBUCKET_ALLOWED_WORKSPACES": "my-ws"}, clear=False)
    def test_bitbucket_token_injected_for_git_ssh_format(self) -> None:
        """Credentials should be injected for git@bitbucket.org:workspace/repo format."""
        loader, module_params = self._make_loader_and_params("git@bitbucket.org:my-ws/my-repo.git")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "bb_test123" in module_params.module_source

    @patch.dict("os.environ", {"BITBUCKET_TOKEN": "bb_test123", "BITBUCKET_ALLOWED_WORKSPACES": "my-ws"}, clear=False)
    def test_bitbucket_token_injected_for_git_https_format(self) -> None:
        """Credentials should be injected for git::https://bitbucket.org/workspace/repo format."""
        loader, module_params = self._make_loader_and_params("git::https://bitbucket.org/my-ws/my-repo.git")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "bb_test123" in module_params.module_source

    @patch.dict("os.environ", {"BITBUCKET_TOKEN": "bb_test123", "BITBUCKET_ALLOWED_WORKSPACES": "my-ws"}, clear=False)
    def test_bitbucket_token_injected_for_git_ssh_protocol_format(self) -> None:
        """Credentials should be injected for git::ssh://git@bitbucket.org/workspace/repo format."""
        loader, module_params = self._make_loader_and_params("git::ssh://git@bitbucket.org/my-ws/my-repo.git")
        result = loader._is_matching_loader(module_params)

        assert result is True
        assert "bb_test123" in module_params.module_source

    def test_bitbucket_no_token_returns_false(self) -> None:
        """When BITBUCKET_TOKEN is not set, _is_matching_loader should return False."""
        loader = BitbucketAccessTokenLoader()
        module_params = _make_module_params("bitbucket.org/my-ws/my-repo")
        loader.discover(module_params)
        # Ensure token is empty (no token set)
        module_params.token = ""
        result = loader._is_matching_loader(module_params)

        assert result is False

    @patch.dict("os.environ", {
        "BITBUCKET_USERNAME": "my-user",
        "BITBUCKET_APP_PASSWORD": "app-pass-123",
        "BITBUCKET_ALLOWED_WORKSPACES": "my-ws",
    }, clear=False)
    def test_bitbucket_app_password_injected_when_workspace_matches(self) -> None:
        """When BITBUCKET_TOKEN is not set but BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD are,
        credentials should be injected when workspace matches."""
        loader = BitbucketAccessTokenLoader()
        module_params = _make_module_params("bitbucket.org/my-ws/my-repo")
        # Ensure BITBUCKET_TOKEN is not set
        with patch.dict("os.environ", {}, clear=False):
            env = dict(**__import__("os").environ)
            env.pop("BITBUCKET_TOKEN", None)
            with patch.dict("os.environ", env, clear=True):
                # Need to re-set the env vars that were cleared
                with patch.dict("os.environ", {
                    "BITBUCKET_USERNAME": "my-user",
                    "BITBUCKET_APP_PASSWORD": "app-pass-123",
                    "BITBUCKET_ALLOWED_WORKSPACES": "my-ws",
                }, clear=False):
                    loader.discover(module_params)
                    result = loader._is_matching_loader(module_params)

        assert result is True
        assert "app-pass-123" in module_params.module_source
        assert "my-user:app-pass-123@bitbucket.org/my-ws/my-repo" in module_params.module_source
