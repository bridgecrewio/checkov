import logging

from yaml import YAMLError

from checkov.kubernetes.parser import k8_yaml, k8_json

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

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
    except YAMLError as err:
        if err.problem in [
            'expected \'<document start>\', but found \'{\'']:
            try:
                (template, template_lines) = k8_json.load(filename)
            except Exception as json_err:  # pylint: disable=W0703
                logger.error(
                    'Template %s is malformed: %s', filename, err.problem)
                pass

    return template, template_lines


