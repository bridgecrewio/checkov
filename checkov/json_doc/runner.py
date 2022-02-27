from checkov.common.output.report import CheckType
from checkov.common.parsers.json import parse
from checkov.common.runners.object_runner import Runner as ObjectRunner


class Runner(ObjectRunner):
    check_type = CheckType.JSON

    def import_registry(self):
        from checkov.json_doc.registry import registry
        return registry

    def _parse_file(self, f):
        return parse(f)

    def get_start_end_lines(self, end, result_config, start):
        start = result_config.start_mark.line
        end = result_config.end_mark.line
        return end, start
