from __future__ import annotations

from typing import List, Dict
from pydantic import BaseModel


class PackageAliasesObject(BaseModel):
    packageAliases: List[str] = list()  # noqa: CCE003  # a static attribute


class FileObject(BaseModel):
    packageAliases: Dict[str, PackageAliasesObject] = dict()  # noqa: CCE003  # a static attribute


class RepositoryObject(BaseModel):
    files: Dict[str, FileObject] = dict()  # noqa: CCE003  # a static attribute


class LanguageObject(BaseModel):
    repositories: Dict[str, RepositoryObject] = dict()  # noqa: CCE003  # a static attribute


class AliasMappingObject(BaseModel):
    languages: Dict[str, LanguageObject] = dict()  # noqa: CCE003  # a static attribute
