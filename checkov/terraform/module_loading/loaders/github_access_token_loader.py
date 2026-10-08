from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING

from checkov.terraform.module_loading.loaders.git_loader import GenericGitLoader

if TYPE_CHECKING:
    from checkov.terraform.module_loading.module_params import ModuleParams

logger = logging.getLogger(__name__)

# Patterns to extract the org/owner from various GitHub URL formats
_GITHUB_ORG_PATTERNS = [
    # git@github.com:org/repo.git
    re.compile(r"git@github\.com:([^/]+)/"),
    # git::ssh://git@github.com/org/repo.git
    re.compile(r"git::ssh://git@github\.com/([^/]+)/"),
    # git::https://github.com/org/repo or https://github.com/org/repo
    re.compile(r"(?:git::)?https?://github\.com/([^/]+)/"),
    # github.com/org/repo (bare prefix)
    re.compile(r"^github\.com/([^/]+)/"),
]


def _extract_github_org(module_source: str) -> str | None:
    """Extract the GitHub organization/owner from a module source URL.

    Handles the following URL formats:
      - github.com/org/repo
      - git::https://github.com/org/repo
      - git@github.com:org/repo
      - git::ssh://git@github.com/org/repo
    """
    for pattern in _GITHUB_ORG_PATTERNS:
        match = pattern.search(module_source)
        if match:
            return match.group(1)
    return None


def _is_org_allowed(org: str | None, allowed_orgs: set[str]) -> bool:
    """Check whether the extracted org is in the allowed set.

    A wildcard entry '*' permits all organizations.
    Comparison is case-insensitive.
    """
    if org is None:
        return False
    if "*" in allowed_orgs:
        return True
    return org.lower() in allowed_orgs


class GithubAccessTokenLoader(GenericGitLoader):
    def discover(self, module_params: ModuleParams) -> None:
        self.module_source_prefix = "github.com"
        module_params.username = "x-access-token"
        module_params.token = os.getenv('GITHUB_PAT', '')

    def _is_matching_loader(self, module_params: ModuleParams) -> bool:
        if module_params.token:
            # Validate that the target org is in the allowed list before injecting credentials
            allowed_orgs_raw = os.getenv("GITHUB_PAT_ALLOWED_ORGS", "")
            if not allowed_orgs_raw:
                self.logger.info(
                    "GITHUB_PAT is set but GITHUB_PAT_ALLOWED_ORGS is not configured. "
                    "Credentials will not be injected. Set GITHUB_PAT_ALLOWED_ORGS to a "
                    "comma-separated list of GitHub orgs/owners (or '*' for all) to enable "
                    "credential injection."
                )
                return False

            allowed_orgs = {org.strip().lower() for org in allowed_orgs_raw.split(",") if org.strip()}
            org = _extract_github_org(module_params.module_source)

            if not _is_org_allowed(org, allowed_orgs):
                self.logger.debug(
                    "GitHub org '%s' extracted from module source is not in GITHUB_PAT_ALLOWED_ORGS; "
                    "credentials will not be injected.",
                    org,
                )
                return False

            # if GITHUB_PAT is set and the org is allowed, convert source (github ssh or github http or generic git)
            # to use the token in generic format git::https://x-access-token:<token>@github.com/org/repo.git
            self.logger.debug("GITHUB_PAT found and org is allowed. Attempting to clone module using HTTP basic authentication.")
            # if module_source = github.com/org/repo
            if module_params.module_source.startswith(self.module_source_prefix):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source}"
                return True
            # if module_source = git::https://github.com/org/repo.git
            if module_params.module_source.startswith(f"git::https://{self.module_source_prefix}"):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source.split('git::https://')[1]}"
                return True
            # if module_source = git@github.com:org/repo.git
            if module_params.module_source.startswith(f"git@{self.module_source_prefix}:"):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source.split('git@')[1].replace(':', '/')}"
                return True
            # if module_source = git::ssh://git@github.com/org/repo.git
            if module_params.module_source.startswith(f"git::ssh://git@{self.module_source_prefix}"):
                module_params.module_source = f"git::https://{module_params.username}:{module_params.token}@{module_params.module_source.split('git::ssh://git@')[1]}"
                return True

        return False


loader = GithubAccessTokenLoader()
