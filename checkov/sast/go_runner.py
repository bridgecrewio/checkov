import ctypes
import json
from os import path
from typing import Dict, Any, Optional


current_dir = path.dirname(path.realpath(__file__))
library = ctypes.cdll.LoadLibrary(path.join(current_dir, '../sast_core/library.so'))
analyze_code = library.analyzeCode
analyze_code.restype = ctypes.c_void_p


def run_go_library(language: str,
                   source_code_file: Optional[str] = None,
                   source_code_dir: Optional[str] = None,
                   policy_file: Optional[str] = None,
                   policy_dir: Optional[str] = None) -> Dict[str, Any]:
    validate_params(**locals())
    document = {
        "source_code_dir": source_code_dir,
        "source_code_file": source_code_file,
        "policy_dir": policy_dir,
        "policy_file": policy_file,
        "language": language,
    }
    # send the document as a byte array of json format
    analyze_code_output = analyze_code(json.dumps(document).encode('utf-8'))

    # we dereference the pointer to a byte array
    analyze_code_bytes = ctypes.string_at(analyze_code_output)

    # convert our byte array to a string
    analyze_code_string = analyze_code_bytes.decode('utf-8')
    result: Dict[str, Any] = json.loads(analyze_code_string)
    return result


def validate_params(language: str,
                    source_code_file: Optional[str] = None,
                    source_code_dir: Optional[str] = None,
                    policy_file: Optional[str] = None,
                    policy_dir: Optional[str] = None) -> None:
    if (not source_code_file and not source_code_dir) or (source_code_file and source_code_dir):
        raise Exception('must provide source code file or dir for sast runner')

    if (not policy_dir and not policy_file) or (policy_dir and policy_file):
        raise Exception('must provide policy file or dir for sast runner')
    if not language:
        raise Exception('must provide a language for sast runner')
