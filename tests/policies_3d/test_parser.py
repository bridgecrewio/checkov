from checkov.policies_3d.checks_parser import Policy3dParser

def test_3d_policy_parser_init(raw_3d_policy):
    # Act
    parser = Policy3dParser(raw_3d_policy)

    # Assert
    assert parser.schema_version == 'v1'
    assert parser.check_definition == [
      {
        "cves": {
          "or": [
            {
              "and": [
                {
                  "risk_factor": "DoS"
                },
                {
                  "risk_factor": "Medium Severity"
                }
              ]
            }
          ]
        }
      },
      {
        "iac": {
          "or": [
            {
              "violation_id": "BC_K8S_1"
            },
            {
              "violation_id": "BC_K8S_23"
            }
          ]
        }
      }
    ]

def test_3d_policy_parser_parse_check_v1(raw_3d_policy, k8s_record_1, cve_1):
  # Arrange
  parser = Policy3dParser(raw_3d_policy)

  # Act
  check = parser.parse(iac_records=[k8s_record_1], cves_reports=[cve_1])

  # Assert
  assert check
  assert check.id == 'BC_3D_500'
  assert check.category == 'Policy3D'
  assert check.guideline == 'guideline_500'
  assert len(check.predicaments) == 1
  assert len(check.predicaments[0].predicaments[0].predicaments[0].predicates) == 2
  assert len(check.predicaments[0].predicaments[1].predicates) == 2