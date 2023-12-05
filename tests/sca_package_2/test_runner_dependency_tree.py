from pathlib import Path
from packaging import version as packaging_version
from checkov.common.bridgecrew.severities import Severities, BcSeverities
from checkov.common.models.enums import CheckResult

EXAMPLES_DIR = Path(__file__).parent / "examples"


def test_run(sca_package_report_dt):
    # given
    report = next(sca_package_report_dt)
    # then
    assert report.check_type == "sca_package"

    assert report.resources == {'package-lock.json.helmet-csp', 'requirements.txt.grpcio_tools', 'requirements.txt.gevent', 'requirements.txt.pymysql', 'requirements.txt.pyyaml', 'requirements.txt.sanic', 'package-lock.json.nconf', 'requirements.txt.pyramid', 'requirements.txt.multidict', 'requirements.txt.aiohttp', 'package-lock.json.cypress', 'requirements.txt.testcontainers', 'package-files/java/maven/normal/pom.xml.junit_junit', 'requirements.txt.requests', 'requirements.txt.tornado', 'package-lock.json.uglify-js', 'package-files/yarn/package.json.node-esapi', 'package-files/yarn/package.json.marked', 'package-lock.json.decode-uri-component', 'package-lock.json.mongodb', 'requirements.txt.django', 'package-lock.json.debug', 'requirements.txt.pika', 'requirements.txt.yarl', 'requirements.txt.protobuf', 'requirements.txt.celery', 'requirements.txt.uvicorn', 'requirements.txt.mysqlclient', 'requirements.txt.elasticsearch', 'package-files/yarn/package.json.needle', 'requirements.txt.fastapi', 'package-lock.json.marked', 'requirements.txt.pymongo', 'package-lock.json.bson', 'requirements.txt.redis', 'package-lock.json.minimist', 'package-lock.json.mocha', 'requirements.txt.kafka-python', 'requirements.txt.wrapt', 'requirements.txt.hug', 'package-lock.json.unset-value', 'package-lock.json.glob-parent', 'package-lock.json.grunt', 'requirements.txt.flask', 'package-files/yarn/package.json.bcrypt-nodejs', 'requirements.txt.contextvars', 'requirements.txt.werkzeug', 'requirements.txt.packaging', 'package-files/java/maven/normal/pom.xml.org.apache.logging.log4j_log4j-core', 'requirements.txt.gunicorn', 'requirements.txt.urllib3', 'requirements.txt.psycopg', 'requirements.txt.streamlit', 'package-files/java/maven/normal/pom.xml.commons-collections_commons-collections'}
    assert len(report.passed_checks) == 34
    assert len(report.failed_checks) == 56
    assert len(report.skipped_checks) == 0
    assert len(report.parsing_errors) == 0

    cve_record = next((c for c in report.failed_checks if
                       c.resource == "package-lock.json.bson"
                       and c.vulnerability_details.get('root_package_name', "") == 'mongodb'
                       and c.check_name == "SCA package scan"), None)
    assert cve_record is not None
    assert cve_record.bc_check_id == 'BC_CVE_2019_2391'
    assert cve_record.check_id == 'CKV_CVE_2019_2391'
    assert cve_record.check_name == "SCA package scan"
    assert cve_record.check_result == {"result": CheckResult.FAILED}
    assert cve_record.code_block == [(0, 'bson: 1.0.9')]
    assert cve_record.description == (
        'Incorrect parsing of certain JSON input may result in js-bson not correctly serializing BSON. '
        'This may cause unexpected application behaviour including data disclosure. '
        'This issue affects: MongoDB Inc. js-bson library version 1.1.3 and prior to.'
    )
    assert cve_record.file_abs_path == f"{EXAMPLES_DIR}/package-lock.json"
    assert cve_record.file_line_range == [0, 0]
    assert cve_record.file_path == "/package-lock.json"
    assert cve_record.repo_file_path == "/tests/sca_package_2/examples/package-lock.json"
    assert cve_record.resource == 'package-lock.json.bson'
    assert cve_record.severity == Severities[BcSeverities.MEDIUM]
    assert cve_record.short_description == 'CVE-2019-2391 - bson: 1.0.9'
    assert cve_record.vulnerability_details["lowest_fixed_version"] == "1.1.4"
    assert cve_record.vulnerability_details["fixed_versions"] == [
        packaging_version.parse("1.1.4"),
    ]
    assert cve_record.vulnerability_details['root_package_name'] == 'mongodb'
    assert cve_record.vulnerability_details['root_package_version'] == '2.2.36'
    assert cve_record.vulnerability_details['root_package_fix_version'] == '3.1.13'
