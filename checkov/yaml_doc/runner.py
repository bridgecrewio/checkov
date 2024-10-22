from __future__ import annotations

from typing import TYPE_CHECKING, Any

from checkov.common.bridgecrew.check_type import CheckType
from checkov.common.parsers.yaml.parser import parse
from checkov.common.runners.object_runner import Runner as ObjectRunner
from checkov.common.util.consts import START_LINE, END_LINE

if TYPE_CHECKING:
    from checkov.common.checks.base_check_registry import BaseCheckRegistry
    from checkov.common.typing import LibraryGraphConnector
    from checkov.common.runners.graph_builder.local_graph import ObjectLocalGraph
    from checkov.common.runners.graph_manager import ObjectGraphManager


class Runner(ObjectRunner):
    check_type = CheckType.YAML  # noqa: CCE003  # a static attribute

    def __init__(
        self,
        db_connector: LibraryGraphConnector | None = None,
        source: str = "yaml",
        graph_class: type[ObjectLocalGraph] | None = None,
        graph_manager: ObjectGraphManager | None = None,
    ) -> None:
        super().__init__(
            db_connector=db_connector,
            source=source,
            graph_class=graph_class,
            graph_manager=graph_manager,
        )
        self.file_extensions = ['.yaml', '.yml']

    def import_registry(self) -> BaseCheckRegistry:
        from checkov.yaml_doc.registry import registry

        return registry

    @staticmethod
    def _parse_file(
        f: str, file_content: str | None = None
    ) -> tuple[dict[str, Any] | list[dict[str, Any]], list[tuple[int, str]]] | None:
        return parse(f, file_content)

    def get_start_end_lines(
        self, end: int, result_config: dict[str, Any] | list[dict[str, Any]], start: int
    ) -> tuple[int, int]:
        if result_config and isinstance(result_config, list):
            if not isinstance(result_config[0], dict):
                return -1, -1
            start = result_config[0]["__startline__"] - 1
            end = result_config[len(result_config) - 1]["__endline__"]
        elif result_config and isinstance(result_config, dict):
            if "__startline__" not in result_config or "__endline__" not in result_config:
                return -1, -1
            start = result_config["__startline__"]
            end = result_config["__endline__"]
        return end, start

    @staticmethod
    def resolve_sub_name(definition: dict[str, Any], start_line: int, end_line: int, tag: str) -> str:
        """
        extract the value of the tag, that is within the line of range(start_line, end_line)

        >>> Runner.resolve_sub_name({"executors":{"image-executor":{"docker":[],"__startline__":8,"__endline__":11}}}, 9, 11, 'executors')
        'image-executor'

        >>> Runner.resolve_sub_name({"jobs":{"job-name":{"docker":[],"__startline__":13,"__endline__":20}}}, 15, 16, 'jobs')
        'job-name'
        """
        if not definition:
            return ""
        tag_value = definition.get(tag) or {}
        for key, sub_name in tag_value.items():
            if key in (START_LINE, END_LINE) or not isinstance(sub_name, dict):
                continue
            if sub_name[START_LINE] <= start_line <= end_line <= sub_name[END_LINE]:
                return str(key)
        return ""

    @staticmethod
    def resolve_step_name(job_definition: dict[str, Any], start_line: int, end_line: int) -> str:
        """
        extract the step name from the given job within the line of range(start_line, end_line)

        >>> Runner.resolve_step_name({"steps":["checkout",{}],"__startline__":42,"__endline__":49}, 48, 49)
        '[1](checkout)'

        >>> Runner.resolve_step_name({"runs-on":"ubuntu-latest","steps":[{"uses":"actions/checkout@v2","__startline__":22,"__endline__":23}]}, 22, 23)
        '[1]'

        >>> Runner.resolve_step_name({"runs-on":"ubuntu-latest","steps":[{"name": "ab","__startline__":22,"__endline__":23}, {"name":"step_name","__startline__":23,"__endline__":33}]}, 23, 33)
        '[2](step_name)'

        """
        if not job_definition:
            return ""
        for idx, step in enumerate([step for step in job_definition.get('steps') or [] if step]):
            if isinstance(step, str):
                return f"[{idx + 1}]({step})"
            elif isinstance(step, dict):
                if step[START_LINE] <= start_line <= end_line <= step[END_LINE]:
                    name = step.get('name')
                    return f"[{idx + 1}]({name})" if name else f"[{idx + 1}]"
        return ""

    @staticmethod
    def resolve_image_name(image_definition: dict[str, Any], start_line: int, end_line: int) -> str:
        """
        extract the image name from the given job definition within the line of range(start_line, end_line)

        >>> Runner.resolve_image_name({"docker":[{"image":"mongo:2.6.8","__startline__":15,"__endline__":16}]}, 15, 16)
        '[1](mongo:2.6.8)'

        """
        if not image_definition:
            return ""
        for idx, step in enumerate([step for step in image_definition.get('docker') or [] if step]):
            if isinstance(image_definition.get('docker'), dict):
                if step == 'image':
                    return f"[{idx + 1}]({image_definition['docker'][step]})"
            if isinstance(step, str):
                return f"[{idx + 1}]({step})"
            elif isinstance(step, dict):
                if step[START_LINE] <= start_line <= end_line <= step[END_LINE]:
                    name = step.get('image')
                    return f"[{idx + 1}]({name})" if name else f"[{idx + 1}]"
        return ""
