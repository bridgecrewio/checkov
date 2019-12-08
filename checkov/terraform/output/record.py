class Record():
    check_id = ""
    check_name = ""
    check_result = None
    code_block = ""
    file_path = ""
    file_line_range = []
    resource = ""

    def __init__(self, check_id, check_name, check_result, code_block, file_path, file_line_range, resource):
        self.check_id = check_id
        self.check_name = check_name
        self.check_result = check_result
        self.code_block = code_block
        self.file_path = file_path
        self.file_line_range = file_line_range
        self.resource = resource
