from __future__ import annotations

from typing import TYPE_CHECKING

from checkov.secrets.parsers.single_line_parser import BaseSingleLineParser

if TYPE_CHECKING:
    from detect_secrets.util.code_snippet import CodeSnippet


class TerraformSingleLineParser(BaseSingleLineParser):
    def ignore_secret(self, raw_context: CodeSnippet) -> bool:
        return self.ignore_terraform_data_block(raw_context=raw_context)

    def ignore_terraform_data_block(self, raw_context: CodeSnippet) -> bool:
        """Check for a possible data block usage"""

        # search backwards to find a possible 'data' block
        for line_index in range(raw_context.target_index - 1, -1, -1):
            if raw_context.lines[line_index].lstrip().startswith('data "'):
                # a data block is typically used to get remote information,
                # therefore can retrieve a secret, but has not a hardcoded secret
                return True

        return False


terraform_single_line_parser = TerraformSingleLineParser()
