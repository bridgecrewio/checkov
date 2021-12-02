# method 'str.removeprefix()' was added in Python 3.9
def removeprefix(input_str: str, prefix: str) -> str:
    if input_str.startswith(prefix):
        return input_str[len(prefix) :]
    return input_str
