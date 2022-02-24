from checkov.common.output.report import CheckType
from checkov.common.parsers.yaml.parser import parse
from checkov.common.runners.object_runner import Runner as ObjectRunner


class Runner(ObjectRunner):
    check_type = CheckType.YAML

    def import_registry(self):
        from checkov.yaml_doc.registry import registry
        return registry

    def _parse_file(self, f):
        parse(f)
