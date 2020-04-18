import logging

from checkov.kubernetes.parser import k8_yaml

logger = logging.getLogger(__name__)

def parse( filename):
    template = None
    template_lines = None
    try:
        (template, template_lines) = k8_yaml.load(filename)
    except IOError as e:
        if e.errno == 2:
            logger.error('Template file not found: %s', filename)
        elif e.errno == 21:
            logger.error('Template references a directory, not a file: %s',
                              filename)
        elif e.errno == 13:
            logger.error('Permission denied when accessing template file: %s',
                              filename)
    except UnicodeDecodeError as err:
        logger.error('Cannot read file contents: %s', filename)
    return template, template_lines
