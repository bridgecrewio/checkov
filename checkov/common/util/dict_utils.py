def getInnerDict(source_dict, path_as_list):
    result = source_dict
    for index in path_as_list:
        result = result[index]
    return result