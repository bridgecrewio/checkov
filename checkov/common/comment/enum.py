import re

COMMENT_REGEX = re.compile(r'(checkov:skip=|bridgecrew:skip=) *([A-Z_\d]+)(:[^\n]+)?')
