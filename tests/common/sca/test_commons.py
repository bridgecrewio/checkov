from checkov.common.sca.commons import normalize_twistcli_language


def test_normalize_twistcli_language_for_gem():
    assert normalize_twistcli_language("gem") == "ruby"


def test_normalize_twistcli_language_for_ruby():
    assert normalize_twistcli_language("ruby") == "ruby"


def test_normalize_twistcli_language_for_empty():
    assert normalize_twistcli_language("") == ""


def test_normalize_twistcli_language_for_invalid():
    assert normalize_twistcli_language("bbb") == "bbb"


def test_normalize_twistcli_language_for_python():
    assert normalize_twistcli_language("python") == "python"
