import re

COMMENT_REGEX = re.compile(r'(checkov:skip=|bridgecrew:skip=|cortex:skip=) *([A-Za-z_\d]+(?:,[A-Za-z_\d]+)*)?(:[^\n]*)?')
