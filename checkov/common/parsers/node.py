from __future__ import annotations

import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Type, Generator

if TYPE_CHECKING:
    from checkov.common.parsers.json.decoder import Mark


LOGGER = logging.getLogger(__name__)


class TemplateAttributeError(AttributeError):
    """ Custom error to capture Attribute Errors in the Template """


class StrNode(str):
    """Node class created based on the input class"""

    def __init__(self, x: str, start_mark: Mark, end_mark: Mark) -> None:
        try:
            super().__init__(x)  # type:ignore[call-arg]
        except TypeError:
            super().__init__()
        self.start_mark = start_mark
        self.end_mark = end_mark

    # pylint: disable=bad-classmethod-argument, unused-argument
    def __new__(cls, x: str, start_mark: Mark | None = None, end_mark: Mark | None = None) -> StrNode:
        return str.__new__(cls, x)

    def __getattr__(self, name: str) -> Any:
        raise TemplateAttributeError(f'{name} is invalid')

    def __deepcopy__(self, memo: dict[int, Any]) -> StrNode:
        result = StrNode(self, self.start_mark, self.end_mark)
        memo[id(self)] = result
        return result

    def __copy__(self) -> StrNode:
        return self


class DictNode(dict):  # type:ignore[type-arg]  # either typing works or runtime, but not both
    """Node class created based on the input class"""

    def __init__(self, x: dict[str, Any], start_mark: Mark, end_mark: Mark):
        try:
            super().__init__(x)
        except TypeError:
            super().__init__()
        self.start_mark = start_mark
        self.end_mark = end_mark
        self.condition_functions = ['Fn::If']

    def __deepcopy__(self, memo: dict[int, Any]) -> DictNode:
        result = DictNode(self, self.start_mark, self.end_mark)
        memo[id(self)] = result
        for k, v in self.items():
            result[deepcopy(k)] = deepcopy(v, memo)

        return result

    def __copy__(self) -> DictNode:
        return self

    def is_function_returning_object(self, _mappings: Any = None) -> bool:
        """
            Check if an object is using a function that could return an object
            Return True when
                Fn::Select:
                - 0  # or any number
                - !FindInMap [mapname, key, value] # or any mapname, key, value
            Otherwise False
        """
        if len(self) == 1:
            for k, v in self.items():
                if k in ['Fn::Select']:
                    if isinstance(v, list):
                        if len(v) == 2:
                            p_v = v[1]
                            if isinstance(p_v, dict):
                                if len(p_v) == 1:
                                    for l_k in p_v.keys():
                                        if l_k == 'Fn::FindInMap':
                                            return True

        return False

    def get(self, key: str, default: Any = None) -> Any:
        """ Override the default get """
        if isinstance(default, dict):
            default = DictNode(default, self.start_mark, self.end_mark)
        return super().get(key, default)

    def get_safe(
        self, key: str, default: Any = None, path: list[str] | None = None, type_t: Type[tuple[Any, ...]] = tuple
    ) -> list[tuple[tuple[Any, ...], list[str]]]:
        """Get values in format"""

        path = path or []
        value = self.get(key, default)
        if not isinstance(value, dict):
            if isinstance(value, type_t) or not type_t:
                return [(value, (path[:] + [key]))]

        results = []
        for sub_v, sub_path in value.items_safe(path + [key]):
            if isinstance(sub_v, type_t) or not type_t:
                results.append((sub_v, sub_path))

        return results

    def items_safe(
        self, path: list[int | str] | None = None, type_t: Type[tuple[Any, ...]] = tuple
    ) -> Generator[tuple[Any, ...], Any, None]:
        """Get items while handling IFs"""

        path = path or []
        if len(self) == 1:
            for k, v in self.items():
                if k == 'Fn::If':
                    if isinstance(v, list):
                        if len(v) == 3:
                            for i, if_v in enumerate(v[1:]):
                                if isinstance(if_v, DictNode):
                                    # yield from if_v.items_safe(path[:] + [k, i - 1])
                                    # Python 2.7 support
                                    for items, p in if_v.items_safe(path[:] + [k, i + 1]):
                                        if isinstance(items, type_t) or not type_t:
                                            yield items, p
                                elif isinstance(if_v, list):
                                    if isinstance(if_v, type_t) or not type_t:
                                        yield if_v, path[:] + [k, i + 1]
                                else:
                                    if isinstance(if_v, type_t) or not type_t:
                                        yield if_v, path[:] + [k, i + 1]
                elif not (k == 'Ref' and v == 'AWS::NoValue'):
                    if isinstance(self, type_t) or not type_t:
                        yield self, path[:]
        else:
            if isinstance(self, type_t) or not type_t:
                yield self, path[:]

    def __getattr__(self, name: str) -> Any:
        raise TemplateAttributeError(f'{name} is invalid')


class ListNode(list):  # type:ignore[type-arg]  # either typing works or runtime, but not both
    """Node class created based on the input class"""

    def __init__(self, x: list[Any], start_mark: Mark, end_mark: Mark) -> None:
        try:
            super().__init__(x)
        except TypeError:
            super().__init__()
        self.start_mark = start_mark
        self.end_mark = end_mark
        self.condition_functions = ['Fn::If']

    def __deepcopy__(self, memo: dict[int, Any]) -> ListNode:
        result = ListNode([], self.start_mark, self.end_mark)
        memo[id(self)] = result
        for v in self:
            result.append(deepcopy(v, memo))

        return result

    def __copy__(self) -> ListNode:
        return self

    def items_safe(
        self, path: list[int | str] | None = None, type_t: Type[tuple[Any, ...]] = tuple
    ) -> Generator[tuple[Any, ...], Any, None]:
        """Get items while handling IFs"""

        path = path or []
        for i, v in enumerate(self):
            if isinstance(v, DictNode):
                for items, p in v.items_safe(path[:] + [i]):
                    if isinstance(items, type_t) or not type_t:
                        yield items, p
            else:
                if isinstance(v, type_t) or not type_t:
                    yield v, path[:] + [i]

    def __getattr__(self, name: str) -> Any:
        raise TemplateAttributeError(f'{name} is invalid')
