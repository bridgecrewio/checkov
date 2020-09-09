from checkov.serverless.base_registry import BaseServerlessRegistry


class Registry(BaseServerlessRegistry):

    def __init__(self):
        super().__init__("function")
