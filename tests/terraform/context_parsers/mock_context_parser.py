from checkov.terraform.context_parsers.base_parser import BaseContextParser

class MockContextParser(BaseContextParser):
    def __init__(self):
        definition_type = 'MOCK'
        self.definition_type = definition_type

    def enrich_definition_block(self, block):
        """
        Enrich the context of a Terraform resource block
        :param block: Terraform resource block, key-value dictionary
        :return: Enriched resource block context
        """
        parsed_file_lines = self._filter_file_lines()

        for i, mock_block in enumerate(block):
            mock_type = next(iter(mock_block.keys()))
            mock_name = next(iter(mock_block[mock_type]))
        if not self.context.get(mock_type):
            self.context[mock_type] = {}
        if not self.context.get(mock_type).get(mock_name):
            self.context[mock_type][mock_name] = {}
        for line_num, line in parsed_file_lines:
            line_tokens = [x.replace('"', "") for x in line.split()]
            if all(x in line_tokens for x in ['mock', mock_type, mock_name]):
                self.context[mock_type][mock_name]["start_line"] = 1
                self.context[mock_type][mock_name]["end_line"] = 5
                self.context[mock_type][mock_name]["code_lines"] = ['ABC','123']
        return self.context