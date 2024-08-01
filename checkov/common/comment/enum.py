import re
import os
from typing import Pattern

from checkov.common.runners.base_runner import strtobool

# Default regex pattern
COMMENT_REGEX = re.compile(r'(checkov:skip=|bridgecrew:skip=) *([A-Za-z_\d]+)(:[^\n]+)?')
# Custom regex pattern if needed
CUSTOM_COMMENT_REGEX = re.compile(r'(checkov:skip=|bridgecrew:skip=) *([A-Za-z_\d]+(?:,[A-Za-z_\d]+)*)*(:[^\n]+)?')


def get_comment_regex() -> Pattern[str]:
    """
    Returns the appropriate regex pattern based on the environment variable.
    """
    use_custom_regex = strtobool(os.getenv('CHECKOV_ALLOW_SKIP_MULTIPLE_ONE_LINE', 'False'))
    return CUSTOM_COMMENT_REGEX if use_custom_regex else COMMENT_REGEX
