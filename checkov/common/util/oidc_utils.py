import re
"""
This file provides utility functions for handling OIDC-related operations, particularly for GitHub repositories.

Constants:
    gh_repo_regex (re.Pattern): A regular expression pattern that matches GitHub repository paths.
        # Matches patterns like: "owner/repo", "${var}/repo", "org.name/repo"
        # Allows for variable substitution syntax ${} and organization names with dots

    gh_abusable_claims (list): A list of GitHub OIDC claims that could potentially be abused in security contexts.
"""
gh_repo_regex = re.compile(r"(\$\{)?[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)*(\})?/[^/]+")
gh_abusable_claims = ["workflow", "environment", "ref", "context", "head_ref", "base_ref"]
