import logging
from yaml import YAMLError

from checkov.kubernetes.parser import k8_yaml, k8_json

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

logger = logging.getLogger(__name__)


def parse(filename):
    template = None
    template_lines = None
    try:
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            (template, template_lines) = k8_yaml.load(filename)
        if filename.endswith(".json"):
            (template, template_lines) = k8_json.load(filename)
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
    except YAMLError as err:
        pass

    return template, template_lines
