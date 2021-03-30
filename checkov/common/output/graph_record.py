from checkov.common.output.record import Record


class GraphRecord(Record):
    breadcrumbs = {}

    def __init__(self, record, breadcrumbs):
        self.check_id = record.check_id
        self.check_name = record.check_name
        self.check_result = record.check_result
        self.code_block = record.code_block
        self.file_path = record.file_path
        self.file_line_range = record.file_line_range
        self.resource = record.resource
        self.evaluations = record.evaluations
        self.check_class = record.check_class
        self.repo_file_path = record.repo_file_path
        self.fixed_definition = record.fixed_definition
        self.entity_tags = record.entity_tags
        self.caller_file_path = record.caller_file_path
        self.caller_file_line_range = record.caller_file_line_range
        self.breadcrumbs = breadcrumbs
