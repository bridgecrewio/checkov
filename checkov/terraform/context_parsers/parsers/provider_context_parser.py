import hcl2

from checkov.terraform.context_parsers.base_parser import BaseContextParser


class ProviderContextParser(BaseContextParser):
    def __init__(self):
        definition_type = "provider"
        super().__init__(definition_type=definition_type)

    def get_entity_context_path(self, entity_block):
        entity_type = next(iter(entity_block))
        return [entity_type] + entity_block[entity_type].get('alias', ['default'])

    def _is_block_signature(self, line_num, line_tokens, entity_context_path):
        # Ignore the alias as it is not part of the signature
        is_provider = super()._is_block_signature(line_num, line_tokens, entity_context_path[0:-1])
        if not is_provider or '=' in line_tokens or line_tokens[0] != 'provider':
            # The line provider = alias is not a provider block although it has the correct words
            # Also skips comments that include words like provider and aws
            return False

        end_line = self._compute_definition_end_line(line_num)
        provider_type = entity_context_path[0]
        provider_obj = hcl2.loads("\n".join(map(lambda obj: obj[1], self.file_lines[line_num - 1:end_line if end_line > line_num else line_num])))['provider'][0]
        alias = provider_obj[provider_type].get('alias', ['default'])
        return super()._is_block_signature(line_num, line_tokens + alias, entity_context_path)


parser = ProviderContextParser()
