import re
import os
from typing import Pattern

from checkov.common.runners.base_runner import strtobool

# Default regex pattern
COMMENT_REGEX = re.compile(r'(checkov:skip=|bridgecrew:skip=) *([A-Za-z_\d]+)(:[^\n]+)?')
# Custom regex pattern if needed
MULTIPLE_CHECKS_SKIP_REGEX = re.compile(r'(checkov:skip=|bridgecrew:skip=) *([A-Za-z_\d]+(?:,[A-Za-z_\d]+)*)*(:[^\n]+)?')


def get_comment_regex(allow_multiple_skips: bool) -> Pattern[str]:
    """
    Returns the appropriate regex pattern based on the environment variable.
    """
    return MULTIPLE_CHECKS_SKIP_REGEX if allow_multiple_skips else COMMENT_REGEX
