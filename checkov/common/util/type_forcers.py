def force_list (var):
    if not isinstance(var, list):
        var = [var]
    return var


def force_int (var):
    if not isinstance(var, int):
        var = int(var)
    return var
