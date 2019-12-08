from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ResourceContextParser(BaseContextParser):
    def __init__(self):
        definition_type = 'RESOURCE'
        super().__init__(definition_type=definition_type)

    def enrich_definition_block(self, block):
        """
        Enrich the context of a Terraform resource block
        :param block: Terraform resource block, key-value dictionary
        :return: Enriched resource block context
        """
        resource_context = {}
        file_lines = self.file_lines
        for i, resource_block in enumerate(block):
            resource_type = next(iter(resource_block.keys()))
            resource_name = next(iter(resource_block[resource_type]))
            self.context[resource_type] = {}
            self.context[resource_type][resource_name] = {}
            for line_num, line in file_lines:
                line_tokens = [x.replace('"', "") for x in line.split()]
                if all(x in line_tokens for x in ['resource', resource_type, resource_name]):
                    self.context[resource_type][resource_name]["start_line"] = line_num
                    self.context[resource_type][resource_name]["end_line"] = self.compute_definition_end_line(line_num)

        return self.context


parser = ResourceContextParser()
