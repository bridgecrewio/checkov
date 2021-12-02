from checkov.common.output.record import Record


class GraphRecord(Record):
    breadcrumbs = {}

    def __init__(self, record, breadcrumbs):
        super().__init__(record.check_id, record.check_name, record.check_result, record.code_block, record.file_path,
                         record.file_line_range, record.resource, record.evaluations, record.check_class,
                         record.file_abs_path, record.entity_tags, record.caller_file_path,
                         record.caller_file_line_range, bc_check_id=record.bc_check_id, resource_address=record.resource_address)
        self.fixed_definition = record.fixed_definition
        self.breadcrumbs = breadcrumbs
