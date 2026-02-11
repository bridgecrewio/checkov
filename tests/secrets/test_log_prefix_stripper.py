import unittest

from checkov.secrets.log_prefix_stripper import (
    strip_log_prefix,
    has_log_prefixes,
    strip_log_prefixes_from_content,
    create_stripped_content,
)
from pathlib import Path

from checkov.secrets.runner import Runner
from detect_secrets.settings import transient_settings


class TestStripLogPrefix(unittest.TestCase):
    """Tests for the strip_log_prefix function."""

    def test_pipe_separated_prefix(self) -> None:
        line = "2026-01-07 09:41:37.553 | DEBUG | crypto      | -----BEGIN RSA PRIVATE KEY-----"
        result = strip_log_prefix(line)
        self.assertEqual(result, "-----BEGIN RSA PRIVATE KEY-----")

    def test_pipe_separated_prefix_with_info(self) -> None:
        line = "2026-01-07 09:41:37.552 | INFO  | crypto      | Decrypting signing key"
        result = strip_log_prefix(line)
        self.assertEqual(result, "Decrypting signing key")

    def test_bracket_style_prefix(self) -> None:
        line = "[2026-01-07 09:41:37] [DEBUG] -----BEGIN RSA PRIVATE KEY-----"
        result = strip_log_prefix(line)
        self.assertEqual(result, "-----BEGIN RSA PRIVATE KEY-----")

    def test_bracket_style_with_module(self) -> None:
        line = "[2026-01-07 09:41:37] [INFO] [crypto] Decrypting signing key"
        result = strip_log_prefix(line)
        self.assertEqual(result, "Decrypting signing key")

    def test_space_separated_prefix(self) -> None:
        line = "2026-01-07 09:41:37.553 DEBUG crypto - -----BEGIN RSA PRIVATE KEY-----"
        result = strip_log_prefix(line)
        self.assertEqual(result, "-----BEGIN RSA PRIVATE KEY-----")

    def test_iso_timestamp_prefix(self) -> None:
        line = "2026-01-07T09:41:37.553Z | INFO  | Starting application"
        result = strip_log_prefix(line)
        self.assertEqual(result, "Starting application")

    def test_time_only_prefix(self) -> None:
        line = "09:41:37.553 | DEBUG | crypto | -----BEGIN RSA PRIVATE KEY-----"
        result = strip_log_prefix(line)
        self.assertEqual(result, "-----BEGIN RSA PRIVATE KEY-----")

    def test_no_prefix(self) -> None:
        line = "-----BEGIN RSA PRIVATE KEY-----"
        result = strip_log_prefix(line)
        self.assertEqual(result, "-----BEGIN RSA PRIVATE KEY-----")

    def test_plain_text_no_prefix(self) -> None:
        line = "This is just a normal line of text"
        result = strip_log_prefix(line)
        self.assertEqual(result, "This is just a normal line of text")

    def test_empty_line(self) -> None:
        result = strip_log_prefix("")
        self.assertEqual(result, "")

    def test_base64_content_preserved(self) -> None:
        line = "2026-01-07 09:41:37.553 | DEBUG | crypto      | MIIEpAIBAAKCAQEAx9TgJ2Zy7KX8rJ3k8PpZrK7aR0L8"
        result = strip_log_prefix(line)
        self.assertEqual(result, "MIIEpAIBAAKCAQEAx9TgJ2Zy7KX8rJ3k8PpZrK7aR0L8")


class TestHasLogPrefixes(unittest.TestCase):
    """Tests for the has_log_prefixes function."""

    def test_log_file_detected(self) -> None:
        content = (
            "2026-01-07 09:41:37.550 | INFO  | main        | Starting application\n"
            "2026-01-07 09:41:37.551 | INFO  | config      | Loading configuration\n"
            "2026-01-07 09:41:37.552 | INFO  | crypto      | Decrypting signing key\n"
            "2026-01-07 09:41:37.553 | DEBUG | crypto      | -----BEGIN RSA PRIVATE KEY-----\n"
            "2026-01-07 09:41:37.553 | DEBUG | crypto      | MIIEpAIBAAKCAQEAx9TgJ2Zy7KX8\n"
        )
        self.assertTrue(has_log_prefixes(content))

    def test_plain_file_not_detected(self) -> None:
        content = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEpAIBAAKCAQEAx9TgJ2Zy7KX8rJ3k8PpZrK7aR0L8\n"
            "-----END RSA PRIVATE KEY-----\n"
        )
        self.assertFalse(has_log_prefixes(content))

    def test_mixed_content_below_threshold(self) -> None:
        content = (
            "This is a normal line\n"
            "Another normal line\n"
            "Yet another normal line\n"
            "2026-01-07 09:41:37.553 | DEBUG | crypto      | one log line\n"
            "More normal content\n"
            "Even more normal content\n"
            "Still normal\n"
            "Normal again\n"
            "Normal once more\n"
            "Final normal line\n"
        )
        self.assertFalse(has_log_prefixes(content))

    def test_empty_content(self) -> None:
        self.assertFalse(has_log_prefixes(""))

    def test_bracket_log_detected(self) -> None:
        content = (
            "[2026-01-07 09:41:37] [INFO] Starting application\n"
            "[2026-01-07 09:41:37] [INFO] Loading configuration\n"
            "[2026-01-07 09:41:37] [DEBUG] Some debug info\n"
        )
        self.assertTrue(has_log_prefixes(content))


class TestStripLogPrefixesFromContent(unittest.TestCase):
    """Tests for the strip_log_prefixes_from_content function."""

    def test_strips_all_prefixes(self) -> None:
        content = (
            "2026-01-07 09:41:37.552 | INFO  | crypto      | Decrypting signing key\n"
            "2026-01-07 09:41:37.553 | DEBUG | crypto      | -----BEGIN RSA PRIVATE KEY-----\n"
            "2026-01-07 09:41:37.553 | DEBUG | crypto      | MIIEpAIBAAKCAQEAx9TgJ2Zy7KX8\n"
            "2026-01-07 09:41:37.553 | DEBUG | crypto      | -----END RSA PRIVATE KEY-----"
        )
        expected = (
            "Decrypting signing key\n"
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIEpAIBAAKCAQEAx9TgJ2Zy7KX8\n"
            "-----END RSA PRIVATE KEY-----"
        )
        result = strip_log_prefixes_from_content(content)
        self.assertEqual(result, expected)


class TestCreateStrippedContent(unittest.TestCase):
    """Tests for the create_stripped_content function."""

    def test_build_log_file(self) -> None:
        test_file = str(Path(__file__).parent / "build_log_prefix" / "build_log_with_private_key.log")
        content = create_stripped_content(test_file)
        self.assertIsNotNone(content)
        self.assertIn("-----BEGIN RSA PRIVATE KEY-----", content)
        # Verify prefixes are removed
        self.assertNotIn("2026-01-07 09:41:37.553 | DEBUG | crypto      | -----BEGIN", content)

    def test_plain_file_not_stripped(self) -> None:
        test_file = str(Path(__file__).parent / "build_log_prefix" / "plain_private_key.txt")
        content = create_stripped_content(test_file)
        self.assertIsNone(content)

    def test_nonexistent_file(self) -> None:
        content = create_stripped_content("/nonexistent/file.log")
        self.assertIsNone(content)

    def test_bracket_log_file(self) -> None:
        test_file = str(Path(__file__).parent / "build_log_prefix" / "bracket_log_with_private_key.log")
        content = create_stripped_content(test_file)
        self.assertIsNotNone(content)
        self.assertIn("-----BEGIN RSA PRIVATE KEY-----", content)
        self.assertNotIn("[2026-01-07 09:41:37]", content)

    def test_putty_key_log_file(self) -> None:
        test_file = str(Path(__file__).parent / "build_log_prefix" / "build_log_with_putty_key.log")
        content = create_stripped_content(test_file)
        self.assertIsNotNone(content)
        self.assertIn("PuTTY-User-Key-File-2: ssh-rsa", content)
        self.assertNotIn("2026-01-07 09:41:37.552 | DEBUG | ssh         | PuTTY", content)


class TestSafeScanWithLogPrefixes(unittest.TestCase):
    """Integration tests verifying _safe_scan detects secrets in build logs."""

    def setUp(self) -> None:
        self.runner = Runner()
        self.plugins_used, self.cleanupFn = self.runner._get_plugins_used()

    def tearDown(self) -> None:
        self.cleanupFn()

    def test_rsa_private_key_in_pipe_log(self) -> None:
        """RSA private key in pipe-separated build log should be detected (CKV_SECRET_13)."""
        with transient_settings({'plugins_used': self.plugins_used}) as settings:
            settings.disable_filters('detect_secrets.filters.heuristic.is_indirect_reference')
            settings.disable_filters('detect_secrets.filters.heuristic.is_potential_uuid')

            _, results = Runner._safe_scan(
                'tests/secrets/build_log_prefix/build_log_with_private_key.log', '.'
            )
        self.assertGreaterEqual(len(results), 1)
        secret_types = {r.type for r in results}
        self.assertIn('Private Key', secret_types)

    def test_rsa_private_key_in_bracket_log(self) -> None:
        """RSA private key in bracket-style build log should be detected (CKV_SECRET_13)."""
        with transient_settings({'plugins_used': self.plugins_used}) as settings:
            settings.disable_filters('detect_secrets.filters.heuristic.is_indirect_reference')
            settings.disable_filters('detect_secrets.filters.heuristic.is_potential_uuid')

            _, results = Runner._safe_scan(
                'tests/secrets/build_log_prefix/bracket_log_with_private_key.log', '.'
            )
        self.assertGreaterEqual(len(results), 1)
        secret_types = {r.type for r in results}
        self.assertIn('Private Key', secret_types)

    def test_putty_key_in_build_log(self) -> None:
        """PuTTY key in build log should be detected (CKV_SECRET_13)."""
        with transient_settings({'plugins_used': self.plugins_used}) as settings:
            settings.disable_filters('detect_secrets.filters.heuristic.is_indirect_reference')
            settings.disable_filters('detect_secrets.filters.heuristic.is_potential_uuid')

            _, results = Runner._safe_scan(
                'tests/secrets/build_log_prefix/build_log_with_putty_key.log', '.'
            )
        self.assertGreaterEqual(len(results), 1)
        secret_types = {r.type for r in results}
        self.assertIn('Private Key', secret_types)

    def test_plain_file_still_detected(self) -> None:
        """Plain file without log prefixes should still detect secrets normally."""
        with transient_settings({'plugins_used': self.plugins_used}) as settings:
            settings.disable_filters('detect_secrets.filters.heuristic.is_indirect_reference')
            settings.disable_filters('detect_secrets.filters.heuristic.is_potential_uuid')

            _, results = Runner._safe_scan(
                'tests/secrets/build_log_prefix/plain_private_key.txt', '.'
            )
        self.assertGreaterEqual(len(results), 1)
        secret_types = {r.type for r in results}
        self.assertIn('Private Key', secret_types)

    def test_mixed_secrets_in_build_log(self) -> None:
        """Both AWS key (single-line) and RSA private key (multiline) should be detected
        in a single build log scan — verifying the file is only scanned once with
        stripped content and both secret types are found."""
        with transient_settings({'plugins_used': self.plugins_used}) as settings:
            settings.disable_filters('detect_secrets.filters.heuristic.is_indirect_reference')
            settings.disable_filters('detect_secrets.filters.heuristic.is_potential_uuid')

            _, results = Runner._safe_scan(
                'tests/secrets/build_log_prefix/build_log_with_mixed_secrets.log', '.'
            )
        secret_types = {r.type for r in results}
        self.assertIn('AWS Access Key', secret_types)
        self.assertIn('Private Key', secret_types)


if __name__ == "__main__":
    unittest.main()
