def force_list (var):
    if not isinstance(var, list):
        var = [var]
    return var