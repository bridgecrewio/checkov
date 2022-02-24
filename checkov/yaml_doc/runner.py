from checkov.common.output.report import CheckType
from checkov.common.parsers.yaml.parser import parse
from checkov.common.runners.object_runner import Runner as ObjectRunner


class Runner(ObjectRunner):
    check_type = CheckType.YAML

    def import_registry(self):
        from checkov.yaml_doc.registry import registry
        return registry

    def _parse_file(self, f):
        content = parse(f)
        return content

    def get_start_end_lines(self, end, result_config, start):
        if result_config and isinstance(result_config, list):
            start = result_config[0]['__startline__']
            end = result_config[len(result_config) - 1]['__endline__']
        elif result_config and isinstance(result_config, dict):
            start = result_config['__startline__']
            end = result_config['__endline__']
        return end, start
