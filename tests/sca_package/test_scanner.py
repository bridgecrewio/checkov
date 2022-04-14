from pathlib import Path
import responses

from checkov.sca_package.scanner import Scanner

EXAMPLES_DIR = Path(__file__).parent / "examples"


def assert_equal_dicts(a, b):
    if set(a.keys()) != set(b.keys()):
        return False

    for key, value in a.items():
        if key not in b:
            return False

        if isinstance(value, list) and not isinstance(value[0], dict):
            if sorted(value) != sorted(b[key]):
                return False
    return True


@responses.activate
def test_run_scan(mock_bc_integration, scan_result2):
    # given
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan",
        json={'id': '2e97f5afea42664309f492a1e2083b43479c2936', 'status': 'running'},
        status=202,
    )

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results/"
                                             "2e97f5afea42664309f492a1e2083b43479c2936",
        json={'outputType': 'Result',
              'outputData': 'H4sIAJYSWGIC/61VS2/bMAz+K4LPjR3ngXbGLkHbYQW6'
                            'rFgfh607KDITa5ElT6LTekX++yjZXdekaLHBF1siCX78+'
                            'NJDZKEyTqKxTZSxKMGySiy4WqGj/89aWihBo4vxHqMDFlX'
                            'cOcjJFG0N4S7WfAWOJN8eImwq8G6qBgujvb3mZZCs5Z10Rm'
                            '3Aein9nCQDUqTxKB62nrF4O4TtAXsNpuRYKYNKLnZgxgST9g'
                            'bjhKyaPSKTPhGAL4zVOxjDOB32CSLv90ik0x7LIRqh9ioeSPS'
                            'HUXGdc7fHYxhP+oNoKk6u9WoHZUQlP+wRxUsGOUeoUao9rKMeK'
                            '0+SX7sAw1GfvaXr8oURSY/i6T9AfCdTYcpKSa4FnDlXh02ja6We'
                            'aU6kQysXlLYA9BAJK1EKrugyJMtCroruWEIu67K7KHPXndBga731I'
                            'ddKg+ULqcjL426TfutFxzenA8pUOhhP0knIlkOOtbeJlvIeciY1o53'
                            'WLTWxcV41jcchE4L2bOvl8jIbx2kyu8nmyew4O08uvtDp+ow+l9l1ck'
                            'x/f55l595NDo4YVR29aKYJJbAHBOap6xXzd25pyXolwwJYKEEsjIWgNJ'
                            'oS63Xzurxo2AKWXtPGyriiXDjGEWmhU8UYGlrxcrUCy5yi9KFqAqi1xI'
                            'L8VY0HXTR01BRBLdDfXQVCLqV4DMosfpC5i9n889VpFqLagM4NOaW0Ac'
                            'EUHOkjHfMPkUVKoDA5UHQF30iyI83t7W30yJaiKLgtFTgXe3moAFCPSQ'
                            'wPWFfep5dpvtuPnfzmpbZUUq+9pECsXJYkepPHmnorXplN4rsiyQG5VM'
                            'l+G1Dm1x+4L3Dol+gLCJ/uv1spwM9ChlnL556EGfNd+KRpu4SaHPDO2L'
                            'XXfOSOLdtd/SnwY38o+wmRVHhBmesotfjvuyb0BlW9UNIVkJ9QzrtZTw'
                            'fpaJAeXqXvsnSaDYdfQ59JJwx5ftuSwnnVJIzuM/L/M6PpizOabre/AT'
                            'v1zNm4CAAA',
              'compressionMethod': 'gzip'},
        status=200
    )

    # when
    result = Scanner().run_scan(
        input_path=Path(EXAMPLES_DIR / "requirements.txt"),
    )

    # then
    assert assert_equal_dicts(result, scan_result2)
    responses.assert_call_count(mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan", 1)
    assert len(responses.calls) >= 2


@responses.activate
def test_run_scan_fail_on_scan(mock_bc_integration):
    # given
    responses.add(
        method=responses.POST,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan",
        json={'id': '2e97f5afea42664309f492a1e2083b43479c2936', 'status': 'running'},
        status=202,
    )

    responses.add(
        method=responses.GET,
        url=mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan-results/"
                                             "2e97f5afea42664309f492a1e2083b43479c2936",
        json={
            "outputType": "Error",
            "outputData": "error_message"
            },
        status=400,
    )

    # when
    result = Scanner().run_scan(
        input_path=Path(EXAMPLES_DIR / "requirements.txt"),
    )

    # then
    assert result == {}
    responses.assert_call_count(mock_bc_integration.bc_api_url + "/api/v1/vulnerabilities/scan", 1)
    assert len(responses.calls) >= 2
