import io
import os
import tarfile
import tempfile

import pytest

from checkov.common.util.file_utils import read_file_safe, get_file_size_safe, extract_tar_archive

def test_sanity_read_file():
    file_to_check = f"{os.path.dirname(os.path.realpath(__file__))}/resources/existing_file"
    file_content = read_file_safe(file_to_check)
    assert file_content == "BLA"


def test_failure_read_file():
    file_to_check = f"non_existing_file"
    file_content = read_file_safe(file_to_check)
    assert file_content == ""


def test_sanity_get_file_size():
    file_to_check = f"{os.path.dirname(os.path.realpath(__file__))}/resources/existing_file"
    file_size = get_file_size_safe(file_to_check)
    assert file_size == 3


def test_failure_get_file_size():
    file_to_check = f"non_existing_file"
    file_size = get_file_size_safe(file_to_check)
    assert file_size == -1


def _build_symlink_traversal_tar() -> bytes:
    """Build a tar with symlink 'out' -> /tmp, then file 'out/canary'."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        link = tarfile.TarInfo("out")
        link.type = tarfile.SYMTYPE
        link.linkname = "/tmp"
        t.addfile(link)
        payload = b"canary\n"
        f = tarfile.TarInfo("out/canary")
        f.size = len(payload)
        t.addfile(f, io.BytesIO(payload))
    return buf.getvalue()


def _build_legitimate_tar() -> bytes:
    """Build a clean tar with only regular relative-path files."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        legit = b"hello\n"
        lf = tarfile.TarInfo("main.tf")
        lf.size = len(legit)
        t.addfile(lf, io.BytesIO(legit))
    return buf.getvalue()


def test_extract_tar_rejects_symlink_traversal_payload():
    """symlink-through-write must be rejected — either by raising an
    exception or by silently dropping the member.  Either way the
    canary must NOT appear outside dest_path."""
    with tempfile.TemporaryDirectory() as tar_dir, tempfile.TemporaryDirectory() as dest_dir:
        tar_path = os.path.join(tar_dir, "problematic.tar.gz")
        with open(tar_path, "wb") as fh:
            fh.write(_build_symlink_traversal_tar())

        # Python ≥3.12 raises an exception; Python <3.12 silently drops the member.
        # Both outcomes are acceptable — what matters is the canary never lands in /tmp.
        try:
            extract_tar_archive(tar_path, dest_dir)
        except Exception:
            pass  # rejection via exception is also correct

        # The canary must NOT have been written outside dest_path
        assert not os.path.exists("/tmp/canary"), (
            "symlink traversal succeeded — canary written to /tmp/canary"
        )


def test_extract_tar_legitimate_files_still_extracted():
    """legitimate files inside the archive must still be extracted normally."""
    with tempfile.TemporaryDirectory() as tar_dir, tempfile.TemporaryDirectory() as dest_dir:
        tar_path = os.path.join(tar_dir, "legit.tar.gz")
        with open(tar_path, "wb") as fh:
            fh.write(_build_legitimate_tar())

        extract_tar_archive(tar_path, dest_dir)

        # main.tf must have been extracted inside dest_dir
        extracted = os.path.join(dest_dir, "main.tf")
        assert os.path.isfile(extracted), "Legitimate file 'main.tf' was not extracted"
        assert open(extracted).read() == "hello\n"
