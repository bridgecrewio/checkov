from typing import Any


class TestSuite:
    def __init__(
        self,
        name: str,
        test_cases: list[TestCase] | None = ...,
        hostname: str | None = ...,
        id: str | None = ...,
        package: str | None = ...,
        timestamp: str | None = ...,
        properties: dict[str, Any] | None =None,
        file: str | None = ...,
        log: str | None = ...,
        url: str | None = ...,
        stdout: str | None = ...,
        stderr: str | None = ...,
    ) -> None: ...


class TestCase:
    def __init__(
        self,
        name: str,
        classname: str | None = ...,
        elapsed_sec: float | None = ...,
        stdout: str | None = ...,
        stderr: str | None = ...,
        assertions: int | None = ...,
        timestamp: str | None = ...,
        status: str | None = ...,
        category: str | None = ...,
        file: str | None = ...,
        line: str | None = ...,
        log: str | None = ...,
        url: str | None = ...,
        allow_multiple_subelements: bool = ...,
    ) -> None: ...

    def add_error_info(
        self, message: str | None = ..., output: str | None = ..., failure_type: str | None = ...
    ) -> None: ...

    def add_failure_info(
        self, message: str | None = ..., output: str | None = ..., failure_type: str | None = ...
    ) -> None: ...

    def add_skipped_info(self, message: str | None = ..., output: str | None = ...) -> None: ...


def to_xml_report_string(test_suites: list[TestSuite], prettyprint: bool = ..., encoding: str | None = ...) -> str: ...
