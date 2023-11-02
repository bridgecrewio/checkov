from typing import Dict, Any, List, Union
from pydantic import BaseModel, create_model

from checkov.common.sast.consts import SastLanguages


class SastPolicyMetadataEntry(BaseModel):
    ID: str  # noqa: CCE003
    Name: str  # noqa: CCE003
    Guidelines: str  # noqa: CCE003
    Category: str  # noqa: CCE003
    Severity: str  # noqa: CCE003
    CWE: List[str]  # noqa: CCE003
    OWASP: Union[List[str], None]  # noqa: CCE003


class SastPolicyEntry(BaseModel):
    Metadata: SastPolicyMetadataEntry  # noqa: CCE003
    Language: SastLanguages  # noqa: CCE003
    Definition: Dict[str, Any]  # noqa: CCE003


# dynamically typing the object of SastPolicies
fields = {lang.value: (List[SastPolicyEntry], []) for lang in SastLanguages}  # type: ignore
SastPolicies = create_model('SastPolicies', **fields)  # type: ignore
