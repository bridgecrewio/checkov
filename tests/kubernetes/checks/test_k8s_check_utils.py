from checkov.kubernetes.checks.resource.k8s.k8s_check_utils import extract_commands


def test_non_int_extract_commands() -> None:
    conf = {'command': ['kube-apiserver', '--encryption-provider-config=config.file']}

    keys, values = extract_commands(conf)
    assert keys == ['kube-apiserver', '--encryption-provider-config']
    assert values == ['', 'config.file']


def test_int_extract_commands() -> None:
    conf = {'command': ['kube-apiserver', '--encryption-provider-config=config.file', '-p', 9082]}

    keys, values = extract_commands(conf)
    assert keys == ['kube-apiserver', '--encryption-provider-config', '-p', 9082]
    assert values == ['', 'config.file', '', '']
