import re

COMMENT_REGEX = re.compile(r'(checkov:skip=|bridgecrew:skip=) *([A-Za-z_\d]+)(:[^\n]+)?')
