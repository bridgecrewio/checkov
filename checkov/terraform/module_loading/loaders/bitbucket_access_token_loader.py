from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader

if TYPE_CHECKING:
    from checkov.terraform.module_loading.module_params import ModuleParams

logger = logging.getLogger(__name__)

# Patterns to extract the workspace/owner from various Bitbucket URL formats
_BITBUCKET_WORKSPACE_PATTERNS = [
    # git@bitbucket.org:workspace/repo.git
    re.compile(r"git@bitbucket\.org:([^/]+)/"),
    # git::ssh://git@bitbucket.org/workspace/repo.git
    re.compile(r"git::ssh://git@bitbucket\.org/([^/]+)/"),
    # git::https://bitbucket.org/workspace/repo or https://bitbucket.org/workspace/repo
    re.compile(r"(?:git::)?https?://bitbucket\.org/([^/]+)/"),
    # bitbucket.org/workspace/repo (bare prefix)
    re.compile(r"^bitbucket\.org/([^/]+)/"),
]


def _extract_bitbucket_workspace(module_source: str) -> str | None:
    """Extract the Bitbucket workspace/owner from a module source URL.

    Handles the following URL formats:
      - bitbucket.org/workspace/repo
      - git::https://bitbucket.org/workspace/repo
      - git@bitbucket.org:workspace/repo
      - git::ssh://git@bitbucket.org/workspace/repo
    """
    for pattern in _BITBUCKET_WORKSPACE_PATTERNS:
        match = pattern.search(module_source)
        if match:
            return match.group(1)
    return None


def _is_workspace_allowed(workspace: str | None, allowed_workspaces: set[str]) -> bool:
    """Check whether the extracted workspace is in the allowed set.

    A wildcard entry '*' permits all workspaces.
    Comparison is case-insensitive.
    """
    if workspace is None:
        return False
    if "*" in allowed_workspaces:
        return True
    return workspace.lower() in allowed_workspaces


class BitbucketAccessTokenLoader(GenericGitLoader):
    def discover(self, module_params: ModuleParams) -> None:
        self.module_source_prefix = "bitbucket.org"
        module_params.username = os.getenv('BITBUCKET_USERNAME', '')
        app_password = os.getenv('BITBUCKET_APP_PASSWORD', '')
        module_params.token = os.getenv('BITBUCKET_TOKEN', '')
        if module_params.token:
            module_params.username = "x-token-auth"
        elif module_params.username and app_password:
            module_params.token = app_password

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        if module_params.token:
            # Validate that the target workspace is in the allowed list before injecting credentials
            allowed_ws_raw = os.getenv("BITBUCKET_ALLOWED_WORKSPACES", "")
            if not allowed_ws_raw:
                self.logger.info(
                    "BITBUCKET_TOKEN is set but BITBUCKET_ALLOWED_WORKSPACES is not configured. "
                    "Credentials will not be injected. Set BITBUCKET_ALLOWED_WORKSPACES to a "
                    "comma-separated list of Bitbucket workspaces/owners (or '*' for all) to "
                    "enable credential injection."
                )
                return False

            allowed_workspaces = {ws.strip().lower() for ws in allowed_ws_raw.split(",") if ws.strip()}
            workspace = _extract_bitbucket_workspace(module_params.module_source)

            if not _is_workspace_allowed(workspace, allowed_workspaces):
                self.logger.debug(
                    "Bitbucket workspace '%s' extracted from module source is not in "
                    "BITBUCKET_ALLOWED_WORKSPACES; credentials will not be injected.",
                    workspace,
                )
                return False

            # Workspace is allowed — inject credentials using the same logic as the parent class
            self.logger.debug(
                "BITBUCKET_TOKEN found and workspace is allowed. "
                "Attempting to clone module using HTTP basic authentication."
            )
            # if module_source = bitbucket.org/workspace/repo
            if module_params.module_source.startswith(self.module_source_prefix):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source}"
                return True
            # if module_source = git::https://bitbucket.org/workspace/repo.git
            if module_params.module_source.startswith(f"git::https://{self.module_source_prefix}"):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source.split('git::https://')[1]}"
                return True
            # if module_source = git@bitbucket.org:workspace/repo.git
            if module_params.module_source.startswith(f"git@{self.module_source_prefix}:"):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source.split('git@')[1].replace(':', '/')}"
                return True
            # if module_source = git::ssh://git@bitbucket.org/workspace/repo.git
            if module_params.module_source.startswith(f"git::ssh://git@{self.module_source_prefix}"):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source.split('git::ssh://git@')[1]}"
                return True

        return False


loader = BitbucketAccessTokenLoader()
