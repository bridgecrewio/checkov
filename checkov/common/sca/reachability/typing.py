from __future__ import annotations

from typing import List, Dict
from pydantic import BaseModel

# {<package_name>: {"packageAliases": [<alias_1> ,..... , <alias_n>]}}
FileParserOutput = Dict[str, Dict[str, List[str]]]


class PackageAliasesObject(BaseModel):
    packageAliases: List[str]


class FileObject(BaseModel):
    packageAliases: Dict[str, PackageAliasesObject] = dict()


class RepositoryObject(BaseModel):
    files: Dict[str, FileObject] = dict()


class LanguageObject(BaseModel):
    repositories: Dict[str, RepositoryObject] = dict()


class AliasMappingObject(BaseModel):
    languages: Dict[str, LanguageObject] = dict()