"""Original code: https://github.com/halfak/deep_merge"""
from __future__ import annotations

from typing import Any, TypeVar, Callable, Protocol

from typing_extensions import TypeAlias  # noqa[TC002]

from checkov.common.util.data_structures_utils import pickle_deepcopy

_T = TypeVar("_T")
_MergeDict = TypeVar("_MergeDict", bound="dict[Any, Any]")
_OverwriteFunc: TypeAlias = "Callable[..., Any]"


class _MergeDictsFunc(Protocol):
    def __call__(
        self,
        d1: _MergeDict,
        d2: _MergeDict,
        *,
        merge_lists: _OverwriteFunc,
        merge_ints: _OverwriteFunc,
        merge_floats: _OverwriteFunc,
        merge_strings: _OverwriteFunc,
        merge_other: _OverwriteFunc,
    ) -> _MergeDict:
        ...


def overwrite(v1: _T, v2: _T, **kwargs: Any) -> _T:
    """
    Completely overwrites one value with another.
    """
    return pickle_deepcopy(v2)


def merge_dicts(
    d1: _MergeDict,
    d2: _MergeDict,
    merge_lists: _OverwriteFunc = overwrite,
    merge_ints: _OverwriteFunc = overwrite,
    merge_floats: _OverwriteFunc = overwrite,
    merge_strings: _OverwriteFunc = overwrite,
    merge_other: _OverwriteFunc = overwrite,
) -> _MergeDict:
    """
    Recursively merges values from d2 into d1.
    """
    kwargs = {
        "merge_lists": merge_lists,
        "merge_ints": merge_ints,
        "merge_floats": merge_floats,
        "merge_strings": merge_strings,
        "merge_other": merge_other,
    }
    for key in d2:
        if key in d1:
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                d1[key] = merge_dicts(d1[key], d2[key], **kwargs)
            elif isinstance(d1[key], list) and isinstance(d2[key], list):
                d1[key] = merge_lists(d1[key], d2[key], **kwargs)
            elif isinstance(d1[key], int) and isinstance(d2[key], int):
                d1[key] = merge_ints(d1[key], d2[key], **kwargs)
            elif isinstance(d1[key], float) and isinstance(d2[key], float):
                d1[key] = merge_ints(d1[key], d2[key], **kwargs)
            elif isinstance(d1[key], str) and isinstance(d2[key], str):
                d1[key] = merge_strings(d1[key], d2[key], **kwargs)
            else:
                d1[key] = merge_other(d1[key], d2[key], **kwargs)
        else:
            d1[key] = overwrite(None, d2[key])

    return d1


def pickle_deep_merge(
    *dicts: _MergeDict,
    merge_dicts: _MergeDictsFunc = merge_dicts,
    merge_lists: _OverwriteFunc = overwrite,
    merge_ints: _OverwriteFunc = overwrite,
    merge_floats: _OverwriteFunc = overwrite,
    merge_strings: _OverwriteFunc = overwrite,
    merge_other: _OverwriteFunc = overwrite,
) -> _MergeDict:
    """
    Recursively merges dictionaries and the datastructures they contain.

    :Parameters:
        *dicts : `dict`
            Dictionaries to be merged.  Items that appear last will take higher
            precedence when merging.
        merge_dicts : `func`
            The function to apply when merging dictionaries.
        merge_lists : `func`
            The function to apply when merging lists.
        merge_ints : `func`
            The function to apply when merging integers.
        merge_floats : `func`
            The function to apply when merging floats.
        merge_strings : `func`
            The function to apply when merging strings.
        merge_other : `func`
            The function to apply when merging other types or types that do not
            match.
    """
    for param in dicts:
        if not isinstance(param, dict):
            raise TypeError("{0} is not a dict".format(param))

    d = dicts[0]
    for d_update in dicts[1:]:
        d = merge_dicts(
            d,
            d_update,
            merge_lists=merge_lists,
            merge_ints=merge_ints,
            merge_floats=merge_floats,
            merge_strings=merge_strings,
            merge_other=merge_other,
        )

    return d
