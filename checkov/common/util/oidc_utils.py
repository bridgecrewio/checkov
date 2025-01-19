import re

gh_repo_regex = re.compile(r"[\w]+/.+")
gh_abusable_claims = ["workflow", "environment", "ref", "context", "head_ref", "base_ref"]
