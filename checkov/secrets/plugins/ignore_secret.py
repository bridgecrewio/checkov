from __future__ import annotations

from typing import TYPE_CHECKING

from detect_secrets.util.filetype import FileType

if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet


def ignore_terraform_data_block(raw_context: CodeSnippet) -> bool:
    """Check for a possible data block usage"""

    # search backwards to find a possible 'data' block
    for line_index in range(raw_context.target_index - 1, -1, -1):
        if raw_context.lines[line_index].lstrip().startswith('data "'):
            # a data block is typically used to get remote information,
            # therefore can retrieve a secret, but has not a hardcoded secret
            return True

    return False


def ignore_secret(
    file_type: FileType,
    context: CodeSnippet | None,
    raw_context: CodeSnippet | None,
) -> bool:
    """Check for false-positive secrets"""

    if not context or not raw_context:
        return False

    if file_type == FileType.TERRAFORM:
        return ignore_terraform_data_block(raw_context=raw_context)

    return False
