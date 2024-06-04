from __future__ import annotations

from typing import Any


def chunk_array(arr: list[Any], per_chunk: int) -> list[list[Any]]:
    result_array: list[list[Any]] = []
    chunk_index = -1

    for index, item in enumerate(arr):
        if index % per_chunk == 0:
            result_array.append([])
            chunk_index += 1
        result_array[chunk_index].append(item)

    return result_array
