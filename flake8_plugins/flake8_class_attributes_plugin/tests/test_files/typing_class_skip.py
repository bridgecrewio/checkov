from typing_extensions import TypedDict, Protocol


class ExampleTypedDict(TypedDict):
    attr_1: str
    attr_2: int


class ExampleProtocol(Protocol):
    attr: str

    def do_something(self) -> str:
        ...
