from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest
from ecdsa import NIST256p
from ecdsa.util import sigdecode_der, sigencode_der

from checkov.common.external_checks.verification import (
    VerificationResult,
    load_public_keys,
    verify_file,
)
from checkov.common.external_checks.verification.trailer_format import (
    TRAILER_PREFIX,
)


_SECP256R1_N = NIST256p.order


def _sign(priv, body: bytes, hashfunc=hashlib.sha256) -> bytes:
    """Produce a DER ECDSA signature over ``body`` using ``hashfunc``."""
    return priv.sign_deterministic(body, hashfunc=hashfunc, sigencode=sigencode_der)


# --------------------------------------------------------------------------
# 1. Python ``ecdsa`` library — sanity baseline.
# --------------------------------------------------------------------------


def test_python_ecdsa_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A signature produced via the standard ``sign_deterministic`` path verifies.

    Baseline interop test — if this fails, nothing else can succeed.
    """
    body = b"def check():\n    pass\n"
    target = tmp_path / "py_signed.py"
    target.write_bytes(make_trailer(body, priv_a))

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, signed = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.OK
    assert signed == body


# --------------------------------------------------------------------------
# 2. OpenSSL CLI — the docs recipe MUST work verbatim.
# --------------------------------------------------------------------------


@pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl CLI not installed")
def test_openssl_dgst_sign_recipe_from_docs_verifies(tmp_path: Path):
    """The exact OpenSSL signing recipe from the customer-facing docs
    must produce a signature the verifier accepts.
    """
    priv_pem = tmp_path / "priv.pem"
    pub_pem = tmp_path / "pub.pem"
    subprocess.run(
        ["openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", str(priv_pem)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["openssl", "ec", "-in", str(priv_pem), "-pubout", "-out", str(pub_pem)],
        check=True, capture_output=True,
    )

    body = b"# openssl-signed check\nID = 'CKV_OSSL_1'\n"
    target = tmp_path / "ossl_signed.py"
    target.write_bytes(body)

    sig_proc = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(priv_pem), str(target)],
        check=True, capture_output=True,
    )
    sig_der = sig_proc.stdout
    hex_payload = sig_der.hex().encode("ascii")

    with open(target, "ab") as f:
        f.write(TRAILER_PREFIX + hex_payload + b"\n")

    result, signed = verify_file(str(target), load_public_keys([str(pub_pem)]))
    assert result == VerificationResult.OK, (
        f"openssl-signed file did not verify; got {result!r}"
    )
    assert signed == body, (
        "verifier returned the wrong bytes — the trailer-stripping step "
        "or the openssl signing step is producing the wrong payload"
    )


# --------------------------------------------------------------------------
# 3. High-S (KMS-style) signatures.
#
# AWS KMS, openssl dgst, and several other production signers emit
# high-S roughly 50% of the time. A verifier that silently rejected
# high-S would break ~half of all customer signatures with no apparent
# pattern.
# --------------------------------------------------------------------------


def _flip_to_high_s(sig_der: bytes) -> bytes:
    """Return a DER signature with ``s`` flipped to its high-S equivalent."""
    r, s = sigdecode_der(sig_der, _SECP256R1_N)
    if s > _SECP256R1_N // 2:
        return sig_der
    high_s = _SECP256R1_N - s
    return sigencode_der(r, high_s, _SECP256R1_N)


def _flip_to_low_s(sig_der: bytes) -> bytes:
    """Return a DER signature with ``s`` flipped to its low-S equivalent."""
    r, s = sigdecode_der(sig_der, _SECP256R1_N)
    if s <= _SECP256R1_N // 2:
        return sig_der
    return sigencode_der(r, _SECP256R1_N - s, _SECP256R1_N)


def test_high_s_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A signature with ``s > n/2`` must verify (the AWS-KMS scenario)."""
    body = b"def check():\n    pass\n"
    raw_sig = _sign(priv_a, body)
    high_s_sig = _flip_to_high_s(raw_sig)
    _r, s = sigdecode_der(high_s_sig, _SECP256R1_N)
    assert s > _SECP256R1_N // 2, "test helper failed to produce a high-S sig"

    target = tmp_path / "high_s.py"
    target.write_bytes(body + TRAILER_PREFIX + high_s_sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, signed = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.OK, (
        f"high-S signature was rejected; verifier got {result!r}. "
        f"This would break ~50% of AWS-KMS-signed customer files. "
        f"Check the low-S enforcement comment in verifier.py."
    )
    assert signed == body


def test_low_s_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """Companion to the high-S test: low-S signatures must also verify."""
    body = b"def check():\n    pass\n"
    raw_sig = _sign(priv_a, body)
    low_s_sig = _flip_to_low_s(raw_sig)
    _r, s = sigdecode_der(low_s_sig, _SECP256R1_N)
    assert s <= _SECP256R1_N // 2, "test helper failed to produce a low-S sig"

    target = tmp_path / "low_s.py"
    target.write_bytes(body + TRAILER_PREFIX + low_s_sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, _ = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.OK


def test_high_s_and_low_s_are_equivalent(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """High-S and low-S forms of the same signature both verify the same payload."""
    body = b"# original\n"
    raw_sig = _sign(priv_a, body)
    high_s = _flip_to_high_s(raw_sig)
    low_s = _flip_to_low_s(raw_sig)

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    for name, sig in (("high_s", high_s), ("low_s", low_s)):
        target = tmp_path / f"{name}.py"
        target.write_bytes(body + TRAILER_PREFIX + sig.hex().encode("ascii") + b"\n")
        result, signed = verify_file(str(target), keys)
        assert result == VerificationResult.OK, f"{name} failed: {result!r}"
        assert signed == body


# --------------------------------------------------------------------------
# 4. Edge-of-range DER signatures: very short and very long but legal.
#
# DER-encoded P-256 sigs vary in length between ~63 and 72 bytes
# depending on leading-zero stripping in r and s.
# --------------------------------------------------------------------------


def test_full_length_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A 70-72-byte (full-length r and s) signature verifies."""
    sig = b""
    final_body = b""
    for i in range(200):
        candidate_body = f"x{i}\n".encode("ascii")
        candidate_sig = _sign(priv_a, candidate_body)
        if len(candidate_sig) >= 70:
            sig = candidate_sig
            final_body = candidate_body
            break
    assert len(sig) >= 70, "could not produce a 70-byte sig in 200 tries"

    target = tmp_path / "full_length.py"
    target.write_bytes(final_body + TRAILER_PREFIX + sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, signed = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.OK
    assert signed == final_body


def test_short_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A short signature (≤ 68 bytes — leading zeros stripped) verifies."""
    sig = b""
    final_body = b""
    for i in range(500):
        candidate_body = f"y{i}\n".encode("ascii")
        candidate_sig = _sign(priv_a, candidate_body)
        if len(candidate_sig) <= 68:
            sig = candidate_sig
            final_body = candidate_body
            break
    if not final_body:
        pytest.skip("could not produce a short sig in 500 tries (rare)")

    target = tmp_path / "short.py"
    target.write_bytes(final_body + TRAILER_PREFIX + sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, signed = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.OK
    assert signed == final_body


# --------------------------------------------------------------------------
# 5. PEM key shape variants.
# --------------------------------------------------------------------------


@pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl CLI not installed")
def test_openssl_generated_pem_loads(tmp_path: Path):
    """A PEM produced by ``openssl ec -in priv.pem -pubout`` loads correctly."""
    priv_pem = tmp_path / "priv.pem"
    pub_pem = tmp_path / "pub.pem"
    subprocess.run(
        ["openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", str(priv_pem)],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["openssl", "ec", "-in", str(priv_pem), "-pubout", "-out", str(pub_pem)],
        check=True, capture_output=True,
    )
    keys = load_public_keys([str(pub_pem)])
    assert len(keys) == 1
    assert keys[0].source_path == str(pub_pem)


def test_ecdsa_generated_pem_loads(tmp_path: Path, priv_a):
    """A PEM produced via ``priv.get_verifying_key().to_pem()`` loads."""
    pub_pem = priv_a.get_verifying_key().to_pem()
    pub_path = tmp_path / "pub.pem"
    pub_path.write_bytes(pub_pem)
    keys = load_public_keys([str(pub_path)])
    assert len(keys) == 1


# --------------------------------------------------------------------------
# 6. Multi-key configurations (rotation scenario).
# --------------------------------------------------------------------------


def test_signature_verifies_against_second_key_in_rotation_list(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, key_b_pub_pem: bytes,
):
    """A signature by ``priv_a`` verifies when keys are configured as ``[b, a]``."""
    body = b"# rotation scenario\n"
    sig = _sign(priv_a, body)
    target = tmp_path / "rotated.py"
    target.write_bytes(body + TRAILER_PREFIX + sig.hex().encode("ascii") + b"\n")

    key_a_path = tmp_path / "a.pem"
    key_a_path.write_bytes(key_a_pub_pem)
    key_b_path = tmp_path / "b.pem"
    key_b_path.write_bytes(key_b_pub_pem)
    keys = load_public_keys([str(key_b_path), str(key_a_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.OK


# --------------------------------------------------------------------------
# 7. Deterministic interop: any valid DER (r, s) encoding verifies.
# --------------------------------------------------------------------------


def test_manually_encoded_dss_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A signature constructed from ``sigencode_der(r, s, n)`` verifies.

    Pins that the verifier accepts ANY valid DER (r, s) encoding, not
    just whatever encoding the producing library happens to emit.
    """
    body = b"# DER round-trip\n"
    raw_sig = _sign(priv_a, body)
    r, s = sigdecode_der(raw_sig, _SECP256R1_N)
    re_encoded = sigencode_der(r, s, _SECP256R1_N)

    target = tmp_path / "reencoded.py"
    target.write_bytes(body + TRAILER_PREFIX + re_encoded.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, signed = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.OK
    assert signed == body


# --------------------------------------------------------------------------
# 8. Signing-input-byte sensitivity.
# --------------------------------------------------------------------------


def test_signing_input_must_match_on_disk_pretrailer_bytes(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """Signature is invalid if signer hashed different bytes than disk."""
    on_disk_body = b"# real body\n"
    fake_signed_payload = b"# different body the signer thought it was signing\n"
    sig = _sign(priv_a, fake_signed_payload)

    target = tmp_path / "mismatched.py"
    target.write_bytes(on_disk_body + TRAILER_PREFIX + sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, _ = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.UNKNOWN_KEY, (
        "verifier accepted a signature over a different payload than the on-disk body"
    )


def test_signing_input_excludes_trailer_line_and_its_newline(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """The bytes the verifier hashes are EXACTLY ``file_bytes[:trailer_start]``.

    Specifically:
    * The terminating ``\\n`` of the body IS included in the signed bytes.
    * The trailer line itself and its terminating ``\\n`` are NOT.
    """
    body = b"line one\nline two\n"
    sig = _sign(priv_a, body)
    target = tmp_path / "exact.py"
    target.write_bytes(body + TRAILER_PREFIX + sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, signed = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.OK
    assert signed == body, (
        f"verifier returned the wrong signed-bytes slice: expected "
        f"{body!r}, got {signed!r}"
    )


# --------------------------------------------------------------------------
# 9. JWS / IEEE P1363 raw ``r||s`` signatures MUST be rejected.
#
# JWT/JWS libraries (PyJWT, jose, java-jwt, …) emit 64-byte flat
# ``r||s`` concatenations, NOT DER. The hex length is 128 chars — INSIDE
# our [126, 144] length guard — so the parser will let the trailer line
# through, and the DER-decode step is the only thing that distinguishes
# the two encodings. The rejection MUST happen via ``BAD_SIGNATURE``
# (well-formed trailer, malformed DER), not ``UNKNOWN_KEY``.
# --------------------------------------------------------------------------


def test_jose_raw_r_s_signature_rejected_as_bad_signature(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A 64-byte raw ``r||s`` signature (the JWS / IEEE P1363 form) is rejected."""
    body = b"def check():\n    return 'ok'\n"
    der_sig = _sign(priv_a, body)
    r, s = sigdecode_der(der_sig, _SECP256R1_N)
    raw_sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    assert len(raw_sig) == 64, "test helper failed to produce a 64-byte raw sig"

    target = tmp_path / "jose_style.py"
    target.write_bytes(body + TRAILER_PREFIX + raw_sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    keys = load_public_keys([str(key_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.BAD_SIGNATURE, (
        f"raw r||s (JWS/IEEE-P1363) signature was not rejected as "
        f"BAD_SIGNATURE; got {result!r}. The verifier accepts ONLY DER."
    )


# --------------------------------------------------------------------------
# 10. Non-SPKI / wrong-curve / wrong-algorithm key shapes are rejected.
#
# Unlike the ``cryptography`` library, ``ecdsa.VerifyingKey.from_pem``
# does NOT cross-check the PEM banner against the body — it only parses
# the body. So a PEM with the legacy ``-----BEGIN EC PUBLIC KEY-----``
# banner wrapped around a valid SPKI body is accepted (the key material
# is the same — no security impact). What MUST still be rejected is any
# key whose curve is not NIST256p.
# --------------------------------------------------------------------------


def test_legacy_banner_with_spki_body_is_accepted(tmp_path: Path, priv_a):
    """A PEM whose banner says ``EC PUBLIC KEY`` but whose body is SPKI is
    accepted — the underlying key material is identical.

    Documents that ``ecdsa.VerifyingKey.from_pem`` is banner-tolerant,
    in contrast to ``cryptography.serialization.load_pem_public_key``.
    """
    spki_pem = priv_a.get_verifying_key().to_pem()
    legacy_pem = (
        spki_pem
        .replace(b"-----BEGIN PUBLIC KEY-----", b"-----BEGIN EC PUBLIC KEY-----")
        .replace(b"-----END PUBLIC KEY-----", b"-----END EC PUBLIC KEY-----")
    )
    pub_path = tmp_path / "legacy_banner.pem"
    pub_path.write_bytes(legacy_pem)
    keys = load_public_keys([str(pub_path)])
    assert len(keys) == 1


def test_garbage_pem_rejected_with_clear_error(tmp_path: Path):
    """A PEM-looking file with no valid SPKI body is rejected."""
    from checkov.common.external_checks.verification.errors import (
        SignatureVerificationError,
    )
    pub_path = tmp_path / "garbage.pem"
    pub_path.write_bytes(
        b"-----BEGIN PUBLIC KEY-----\nnot-base64-at-all\n-----END PUBLIC KEY-----\n"
    )
    with pytest.raises(SignatureVerificationError, match="unsupported key format"):
        load_public_keys([str(pub_path)])


# --------------------------------------------------------------------------
# 11. Wrong hash algorithm on the signing side.
#
# The verifier hardcodes SHA-256. A signature computed with SHA-384 or
# SHA-512 is structurally valid (DER) but cryptographically invalid for
# the payload-under-SHA-256, so the verifier must reject with
# ``UNKNOWN_KEY``.
# --------------------------------------------------------------------------


def test_sha384_signed_file_is_rejected(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A signature computed with SHA-384 over the payload is rejected."""
    body = b"# wrong-hash signer\n"
    sha384_sig = _sign(priv_a, body, hashfunc=hashlib.sha384)

    target = tmp_path / "sha384.py"
    target.write_bytes(body + TRAILER_PREFIX + sha384_sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, _ = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.UNKNOWN_KEY, (
        f"SHA-384-signed file produced {result!r}; expected UNKNOWN_KEY. "
        f"If the verifier ever silently accepts non-SHA-256 hashes, "
        f"that's a primitive-pinning regression."
    )


def test_sha512_signed_file_is_rejected(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """Companion to the SHA-384 test — SHA-512 is also rejected."""
    body = b"# wrong-hash signer (sha512)\n"
    sha512_sig = _sign(priv_a, body, hashfunc=hashlib.sha512)

    target = tmp_path / "sha512.py"
    target.write_bytes(body + TRAILER_PREFIX + sha512_sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, _ = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.UNKNOWN_KEY


# --------------------------------------------------------------------------
# 12. Pre-hashed signing path (operator misconfiguration).
# --------------------------------------------------------------------------


def test_pre_hashed_signature_rejected(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A signature over ``sha256(body)`` (instead of ``body``) is rejected.

    The classic double-hash signing mistake.
    """
    body = b"# pre-hashed signing mistake\n"
    digest = hashlib.sha256(body).digest()
    sig = _sign(priv_a, digest)

    target = tmp_path / "double_hashed.py"
    target.write_bytes(body + TRAILER_PREFIX + sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, _ = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.UNKNOWN_KEY, (
        f"double-hash signing mistake produced {result!r}; expected "
        f"UNKNOWN_KEY. Customer support tickets for this scenario need "
        f"the dedicated diagnostic."
    )
