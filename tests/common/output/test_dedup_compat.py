import unittest

from checkov.common.models.enums import CheckResult
from checkov.common.output.dedup_compat import dedup_reports, dedup_to_upstream_identity, upstream_identity
from checkov.common.output.record import Record
from checkov.common.output.report import Report, remove_duplicate_results


def record(check_id: str, resource: str, chain: tuple, result: CheckResult = CheckResult.FAILED,
           tag: str = "") -> Record:
    rec = Record(check_id=check_id, check_name="n", check_result={"result": result}, code_block=[],
                 file_path="/modules/app/main.tf", file_line_range=[1, 5], resource=resource, evaluations=None,
                 check_class="", file_abs_path="/repo/modules/app/main.tf", entity_tags={"tag": tag})
    rec.module_chain = chain
    return rec


TENANT = (("/repo/tenant/main.tf", "app", ""),)
METRO = (("/repo/metro/main.tf", "app", ""),)
APILOT = (("/repo/apilot/main.tf", "app", ""),)


class TestDedupCompat(unittest.TestCase):
    def test_one_record_per_upstream_identity(self):
        report = Report("terraform")
        for chain in (TENANT, METRO, APILOT):
            report.add_record(record("CKV_1", "module.app.x.y", chain))
        report = remove_duplicate_results(report)
        self.assertEqual(len(report.failed_checks), 3)

        dedup_to_upstream_identity(report)
        self.assertEqual(len(report.failed_checks), 1)

    def test_keeps_the_instance_with_the_greatest_module_chain(self):
        report = Report("terraform")
        report.add_record(record("CKV_1", "module.app.x.y", TENANT, tag="tenant"))
        report.add_record(record("CKV_1", "module.app.x.y", APILOT, tag="apilot"))
        report.add_record(record("CKV_1", "module.app.x.y", METRO, tag="metro"))

        kept = dedup_to_upstream_identity(report).failed_checks
        self.assertEqual(kept[0].module_chain, TENANT)
        self.assertEqual(kept[0].entity_tags, {"tag": "tenant"})

    def test_choice_does_not_depend_on_record_order(self):
        chains = [TENANT, METRO, APILOT]
        kept = set()
        for rotation in range(3):
            report = Report("terraform")
            for chain in chains[rotation:] + chains[:rotation]:
                report.add_record(record("CKV_1", "module.app.x.y", chain))
            kept.add(dedup_to_upstream_identity(report).failed_checks[0].module_chain)
        self.assertEqual(kept, {TENANT})

    def test_distinct_upstream_identities_are_kept(self):
        report = Report("terraform")
        report.add_record(record("CKV_1", "module.app.x.y", TENANT))
        report.add_record(record("CKV_2", "module.app.x.y", TENANT))
        report.add_record(record("CKV_1", "module.app.x.z", TENANT))
        report.add_record(record("CKV_1", "module.app.x.y", TENANT, result=CheckResult.PASSED))
        dedup_to_upstream_identity(report)
        self.assertEqual(len(report.failed_checks), 3)
        self.assertEqual(len(report.passed_checks), 1)

    def test_skipped_records_are_kept_per_instance_as_upstream_does(self):
        report = Report("terraform")
        for chain in (TENANT, METRO):
            report.add_record(record("CKV_1", "module.app.x.y", chain, result=CheckResult.SKIPPED))
        self.assertEqual(len(dedup_to_upstream_identity(report).skipped_checks), 2)

    def test_records_without_module_chain_are_unchanged(self):
        report = Report("terraform")
        report.add_record(record("CKV_1", "aws_s3_bucket.a", ()))
        report.add_record(record("CKV_1", "aws_s3_bucket.b", ()))
        self.assertEqual(len(dedup_to_upstream_identity(report).failed_checks), 2)

    def test_identity_matches_upstream_unique_string(self):
        rec = record("CKV_1", "module.app.x.y", ())
        self.assertEqual(upstream_identity(rec), rec.get_unique_string())

    def test_accepts_a_list_of_reports(self):
        report = Report("terraform")
        report.add_record(record("CKV_1", "module.app.x.y", TENANT))
        report.add_record(record("CKV_1", "module.app.x.y", METRO))
        result = dedup_reports([report])
        self.assertEqual(len(result[0].failed_checks), 1)


if __name__ == "__main__":
    unittest.main()
