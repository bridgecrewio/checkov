# from __future__ import annotations
#
# from typing import List, Dict
# from pydantic import BaseModel
#
#
# class PackageAliasesObject(BaseModel):
#     packageAliases: List[str] = list()  # noqa: CCE003  # a default value for initialization
#
#
# class FileObject(BaseModel):
#     packageAliases: Dict[str, PackageAliasesObject] = dict()  # noqa: CCE003  # a default value for initialization
#
#
# class RepositoryObject(BaseModel):
#     files: Dict[str, FileObject] = dict()  # noqa: CCE003  # a default value for initialization
#
#
# class LanguageObject(BaseModel):
#     repositories: Dict[str, RepositoryObject] = dict()  # noqa: CCE003  # a default value for initialization
#
#
# class AliasMappingObject(BaseModel):
#     languages: Dict[str, LanguageObject] = dict()  # noqa: CCE003  # a default value for initialization
