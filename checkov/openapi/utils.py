import re

VALID_URL_REGEX = re.compile(r'^(https?):\/\/(-\.)?((?!\/\S*)[^\s\/?\.#-]+([-\.\/])?)+(\/\S*)?$')
