# Reverse order
def pytest_collection_modifyitems(session, config, items):
    items[:] = items[::-1]
