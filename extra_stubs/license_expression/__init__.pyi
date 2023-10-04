from pathlib import Path
from typing import Any

from boolean import BooleanAlgebra, Expression as LicenseExpression

class Licensing(BooleanAlgebra):
    def parse(
        self,
        expression: bytes | str | LicenseExpression | None,
        validate: bool = ...,
        strict: bool = ...,
        simple: bool = ...,
        **kwargs: Any,
    ) -> LicenseExpression | None: ...

def get_spdx_licensing(license_index_location: str | Path = ...) -> Licensing: ...
