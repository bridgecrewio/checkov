from datetime import datetime


class UpdateChecker:
    def __init__(self, *, bypass_cache: bool = ...) -> None: ...

    def check(self, package_name: str, package_version: str) -> UpdateResult: ...

class UpdateResult:
    available_version: str
    package_name: str
    release_date: datetime | None
    running_version: str

    def __init__(self, package: str, running: str, available: str, release_date: str): ...
