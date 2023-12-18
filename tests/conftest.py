# Reverse order
def pytest_collection_modifyitems(session, config, items):
    print(" -------------------- Reversing tests order --------------------")
    items[:] = items[::-1]
