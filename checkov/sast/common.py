from __future__ import annotations

from typing import List, Tuple


def get_code_block_from_start(lines: List[str], start: int) -> List[Tuple[int, str]]:
    code_block = [(index, line) for index, line in enumerate(lines, start=start)]
    return cut_code_block_ident(code_block)


def cut_code_block_ident(code_block: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
    min_ident = len(code_block[0][1]) - len(code_block[0][1].lstrip())
    for item in code_block[1:]:
        current_min_ident = len(item[1]) - len(item[1].lstrip())
        if current_min_ident < min_ident:
            min_ident = current_min_ident

    if min_ident == 0:
        return code_block

    code_block_cut_ident = []
    for item in code_block:
        code_block_cut_ident.append((item[0], item[1][min_ident:]))
    return code_block_cut_ident
