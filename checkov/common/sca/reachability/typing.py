from typing import List, Dict

# {<package_name>: {"packageAliases": [<alias_1> ,..... , <alias_n>]}}
FileParserOutput = Dict[str, Dict[str, List[str]]]