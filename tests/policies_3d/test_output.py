from __future__ import annotations

import re

from checkov.policies_3d.output import create_cli_output

ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')


def test_create_simple_cli_output(policy_3d_record_single_iac_single_cve):
    # given
    records = [policy_3d_record_single_iac_single_cve]

    # when
    cli_output = create_cli_output(records)
    cli_output_without_ansci_colors = ansi_escape.sub('', cli_output)

    # then
    assert cli_output_without_ansci_colors == "".join(
        [
            'Check: BC_P3D_1: "3d policy 1"\n',
            '\tSeverity: LOW\n',
            '\tGuide: https://docs.bridgecrew.io/docs/bc_p3d_1\n',
            '\n',
            '\tResource: /dir_a/dir_b/file1.yaml:Pod.default.testPod1\n',
            '\t\t1  | apiVersion: v1\n',
            '\t\t2  | kind: Pod\n',
            '\t\t3  | metadata:\n',
            '\t\t4  |   name: 3d-policy-3\n',
            '\t\t5  | spec:\n',
            '\t\t6  |   containers:\n',
            '\t\t7  |     - name: demo 1\n',
            '\t\t8  |       image: ubuntu:latest\n',
            '\t\t9  |       securityContext:\n',
            '\t\t10 |         runAsNonRoot: false\n',
            '\t\t11 |     - name: demo 2\n',
            '\t\t12 |       image: ubuntu:latest\n',
            '\t\t13 |       securityContext:\n',
            '\t\t14 |         runAsUser: 0\n',
            '\t\t15 |     - name: demo 3\n',
            '\t\t16 |       image: ubuntu:latest\n',
            '\n',
            '\n',
            '\tMatching IaC violations:\n',
            '\t┌──────────────────────────┬──────────────────────────┬─────────────────────────────────────────────────────┬──────────────────────────┐\n',
            '\t│ Resource                 │ Violation                │ Title                                               │ Severity                 │\n',
            '\t├──────────────────────────┼──────────────────────────┼─────────────────────────────────────────────────────┼──────────────────────────┤\n',
            '\t│ Pod.default.testPod1     │ BC_K8S_1                 │ Check 1 title                                       │ MEDIUM                   │\n',
            '\t└──────────────────────────┴──────────────────────────┴─────────────────────────────────────────────────────┴──────────────────────────┘\n',
            '\n',
            '\tImage Referenced with Matching CVEs:\n',
            '\t┌──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┐\n',
            '\t│ Image                    │ Package                  │ Current version          │ CVE ID                   │ Severity                 │\n',
            '\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┤\n',
            '\t│ ubuntu:latest            │ krb5                     │ 1.19.2-2                 │ CVE-2022-42898           │ MEDIUM                   │\n',
            '\t└──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┘\n'
        ]
    )


def test_create_complex_cli_output(policy_3d_record_multi_iac_multi_cve):
    # given
    records = [policy_3d_record_multi_iac_multi_cve]

    # when
    cli_output = create_cli_output(records)
    cli_output_without_ansci_colors = ansi_escape.sub('', cli_output)

    # then
    assert cli_output_without_ansci_colors == "".join(
        ['Check: BC_P3D_1: "3d policy 1"\n',
         '\tSeverity: LOW\n',
         '\tGuide: https://docs.bridgecrew.io/docs/bc_p3d_1\n',
         '\n', '\tResource: /dir_a/dir_b/file1.yaml:Pod.default.testPod1\n', '\t\t1  | apiVersion: v1\n',
         '\t\t2  | kind: Pod\n',
         '\t\t3  | metadata:\n',
         '\t\t4  |   name: 3d-policy-3\n',
         '\t\t5  | spec:\n',
         '\t\t6  |   containers:\n',
         '\t\t7  |     - name: demo 1\n',
         '\t\t8  |       image: ubuntu:latest\n',
         '\t\t9  |       securityContext:\n',
         '\t\t10 |         runAsNonRoot: false\n',
         '\t\t11 |     - name: demo 2\n',
         '\t\t12 |       image: ubuntu:latest\n',
         '\t\t13 |       securityContext:\n',
         '\t\t14 |         runAsUser: 0\n',
         '\t\t15 |     - name: demo 3\n',
         '\t\t16 |       image: ubuntu:latest\n',
         '\n',
         '\n',
         '\tResource: /dir_a/dir_b/file2.yaml:Pod.default.testPod2\n',
         '\t\t1  | apiVersion: v1\n',
         '\t\t2  | kind: Pod\n',
         '\t\t3  | metadata:\n',
         '\t\t4  |   name: 3d-policy-3\n',
         '\t\t5  | spec:\n',
         '\t\t6  |   containers:\n',
         '\t\t7  |     - name: demo 1\n',
         '\t\t8  |       image: image-with-no-cves\n',
         '\t\t9  |       securityContext:\n',
         '\t\t10 |         runAsNonRoot: false\n',
         '\t\t11 |     - name: demo 2\n',
         '\t\t12 |       image: ubuntu:latest\n',
         '\t\t13 |       securityContext:\n',
         '\t\t14 |         runAsUser: 0\n',
         '\t\t15 |     - name: demo 3\n',
         '\t\t16 |       image: ubuntu:latest\n',
         '\n',
         '\n',
         '\tMatching IaC violations:\n',
         '\t┌──────────────────────────┬──────────────────────────┬─────────────────────────────────────────────────────┬──────────────────────────┐\n',
         '\t│ Resource                 │ Violation                │ Title                                               │ Severity                 │\n',
         '\t├──────────────────────────┼──────────────────────────┼─────────────────────────────────────────────────────┼──────────────────────────┤\n',
         '\t│ Pod.default.testPod1     │ BC_K8S_1                 │ Check 1 title                                       │ MEDIUM                   │\n',
         '\t│                          │ BC_K8S_2                 │ Check 2 title                                       │ LOW                      │\n',
         '\t├──────────────────────────┼──────────────────────────┼─────────────────────────────────────────────────────┼──────────────────────────┤\n',
         '\t│ Pod.default.testPod2     │ BC_K8S_3                 │ Check 3 title                                       │ HIGH                     │\n',
         '\t└──────────────────────────┴──────────────────────────┴─────────────────────────────────────────────────────┴──────────────────────────┘\n',
         '\n',
         '\tImage Referenced with Matching CVEs:\n',
         '\t┌──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┬──────────────────────────┐\n',
         '\t│ Image                    │ Package                  │ Current version          │ CVE ID                   │ Severity                 │\n',
         '\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┤\n',
         '\t│ ubuntu:latest            │ krb5                     │ 1.19.2-2                 │ CVE-2022-42898           │ MEDIUM                   │\n',
         '\t├──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┼──────────────────────────┤\n',
         '\t│ ubuntu:latest            │ systemd                  │ 249.11-0ubuntu3.6        │ CVE-2022-3821            │ MEDIUM                   │\n',
         '\t└──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┘\n']
    )


def test_create_empty_cli_output():
    # given
    records = []

    # when
    cli_output = create_cli_output(records)

    # then
    assert cli_output == ''