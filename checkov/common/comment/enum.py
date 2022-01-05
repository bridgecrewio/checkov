import re

COMMENT_REGEX = re.compile(r'(checkov:skip=|bridgecrew:skip=) *([a-zA-Z\d_]+)(:[^\n]+)?')
