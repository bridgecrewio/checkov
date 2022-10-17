from typing import TextIO

from typing_extensions import TypedDict


class _Instruction(TypedDict):
    instruction: str
    startline: int
    endline: int
    content: str
    value: str


class DockerfileParser:
    def __init__(
        self,
        path: str | None = ...,
        cache_content: bool = ...,
        env_replace: bool = ...,
        parent_env: dict[str, str] | None = None,
        fileobj: TextIO | None = None,
        build_args: dict[str, str] | None = None,
    ) -> None: ...

    @property
    def lines(self) -> list[str]: ...

    @property
    def structure(self) -> list[_Instruction]: ...
