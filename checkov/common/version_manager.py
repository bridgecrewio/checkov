from update_checker import UpdateChecker


def check_for_update(package, version):
    try:
        checker = UpdateChecker()
        result = checker.check(package, version)
        return result.available_version
    except Exception:  # nosec
        return None
