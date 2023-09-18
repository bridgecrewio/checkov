from typing import List, Dict, TypedDict


class PackageAliasesObject(TypedDict):
    packageAliases: List[str]


FileParserOutput = Dict[str, PackageAliasesObject]  # key is the package name
