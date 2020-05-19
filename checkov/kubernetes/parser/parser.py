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
        if template:
            if isinstance(template, list):
                for i in range(len(template)):
                    if isinstance(template[i], dict):
                        if not ('apiVersion' in template[i].keys() and 'kind' in template[i].keys()):
                            return
                    else:
                        return
            else:
                return
        else:
            return
    except IOError as e:
        if e.errno == 2:
            logger.error('Template file not found: %s', filename)
            return
        elif e.errno == 21:
            logger.error('Template references a directory, not a file: %s',
                         filename)
            return
        elif e.errno == 13:
            logger.error('Permission denied when accessing template file: %s',
                         filename)
            return
    except UnicodeDecodeError as err:
        logger.error('Cannot read file contents: %s', filename)
        return
    except YAMLError as err:
        return

    return template, template_lines
