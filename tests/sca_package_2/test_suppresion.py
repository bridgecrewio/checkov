from checkov.sca_package_2.suppression import extract_requirements_txt_suppressions


def test_extract_requirements_txt_suppressions():
    # given
    file_content = """
    # checkov:skip=CVE-2019-19844: ignore it
    # checkov:skip=jinja2: don't care
    # checkov:skip=django[CVE-2016-6186,CVE-2021-33203]: really ignore it
    django==1.2
    jinja2==3.1.0
    markupsafe==2.1.1
    """

    # when
    suppressions = extract_requirements_txt_suppressions(content=file_content)

    # then
    assert suppressions == {
        "cve": {
            "CVE-2019-19844": {"suppress_comment": " ignore it", "line_number": 1},
        },
        "package": {
            "jinja2": {"suppress_comment": " don't care", "line_number": 2},
            "django": {
                "CVE-2016-6186": {"suppress_comment": " really ignore it", "line_number": 3},
                "CVE-2021-33203": {"suppress_comment": " really ignore it", "line_number": 3},
            },
        },
    }
