"""Cross-tool signature interoperability tests.

The verifier must accept any DER ECDSA-P256-SHA256 signature produced
by ANY conforming tool. The two production scenarios we have to
guarantee compatibility with are:

1. Python ``cryptography`` library — what tests, internal scripts and
   the docstrings reference.
2. ``openssl dgst -sha256 -sign`` — what the customer-facing docs
   recipe uses, and what most CI signing scripts call.

A third class — HSMs / AWS KMS / cloud KMSes — also emit DER P-256
signatures and is implicitly covered by the **high-S** test, because
KMS implementations produce ``s > n/2`` roughly half the time (the
single biggest interop gotcha for ECDSA DER signatures).

The tests in this file are deliberately mechanism-focused: they construct
or invoke each signer, then push the output through the production
``verify_file`` path with no shortcuts.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)

from checkov.common.external_checks.verification import (
    VerificationResult,
    load_public_keys,
    verify_file,
)
from checkov.common.external_checks.verification.trailer_format import (
    TRAILER_PREFIX,
)


# secp256r1 group order (must match the verifier's constant).
_SECP256R1_N = int(
    "ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551",
    16,
)


# --------------------------------------------------------------------------
# 1. Python ``cryptography`` library — sanity baseline.
# --------------------------------------------------------------------------


def test_python_cryptography_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes, make_trailer,
):
    """A signature produced by ``priv.sign(payload, ec.ECDSA(SHA256()))`` verifies.

    This is the baseline interop test — if this fails, nothing else in
    this file can succeed.
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

    Pinning the recipe end-to-end protects against:

    * a future docs update that introduces a non-portable shell step;
    * a verifier change that tightens the wire format in a way the
      recipe no longer satisfies;
    * a verifier change that subtly breaks the openssl-style hex output
      (e.g. by upper-casing the hex alphabet).
    """
    # Generate a P-256 keypair via OpenSSL (mirrors the docs).
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

    # 1) Produce the DER signature via openssl dgst.
    sig_proc = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(priv_pem), str(target)],
        check=True, capture_output=True,
    )
    sig_der = sig_proc.stdout

    # 2) Encode as the lowercase single-line hex the docs recipe produces:
    #    ``od -An -tx1 | tr -d ' \n'``.
    hex_payload = sig_der.hex().encode("ascii")

    # 3) Append the trailer line.
    with open(target, "ab") as f:
        f.write(TRAILER_PREFIX + hex_payload + b"\n")

    # 4) Push through the production verifier.
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
# The verifier MUST accept signatures where ``s > n/2``. AWS KMS, openssl
# dgst, and several other production signers emit high-S roughly 50% of
# the time. A verifier that silently rejected high-S would break ~half
# of all customer signatures with no apparent pattern.
# --------------------------------------------------------------------------


def _flip_to_high_s(sig_der: bytes) -> bytes:
    """Return a DER signature with ``s`` flipped to its high-S equivalent.

    ECDSA signature equivalence: if ``(r, s)`` verifies a payload under
    a key, ``(r, n - s)`` verifies the same payload under the same key.
    One of them is below ``n/2`` (low-S) and the other is above (high-S).
    This helper produces whichever is the high-S half so the verifier
    test sees a guaranteed-high-S signature.
    """
    r, s = decode_dss_signature(sig_der)
    if s > _SECP256R1_N // 2:
        return sig_der  # already high-S
    high_s = _SECP256R1_N - s
    return encode_dss_signature(r, high_s)


def _flip_to_low_s(sig_der: bytes) -> bytes:
    """Return a DER signature with ``s`` flipped to its low-S equivalent."""
    r, s = decode_dss_signature(sig_der)
    if s <= _SECP256R1_N // 2:
        return sig_der  # already low-S
    return encode_dss_signature(r, _SECP256R1_N - s)


def test_high_s_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A signature with ``s > n/2`` must verify (the AWS-KMS scenario).

    A regression that "tightens security" by adding low-S enforcement
    would break this test loudly.
    """
    body = b"def check():\n    pass\n"
    raw_sig = priv_a.sign(body, ec.ECDSA(hashes.SHA256()))
    high_s_sig = _flip_to_high_s(raw_sig)
    # Confirm we actually constructed a high-S sig.
    _r, s = decode_dss_signature(high_s_sig)
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
    """A signature with ``s <= n/2`` must also verify (companion test).

    Together with the high-S test this proves the verifier treats both
    halves of the S range identically.
    """
    body = b"def check():\n    pass\n"
    raw_sig = priv_a.sign(body, ec.ECDSA(hashes.SHA256()))
    low_s_sig = _flip_to_low_s(raw_sig)
    _r, s = decode_dss_signature(low_s_sig)
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
    """For the same payload + same key, both the high-S and low-S
    forms of a signature must produce the same ``OK`` result.

    A regression where the high-S branch ignores the payload check would
    fail this test: one of the two forms would verify against the
    *wrong* body. The bodies here differ so a payload-ignoring verifier
    would mismatch.
    """
    body = b"# original\n"
    raw_sig = priv_a.sign(body, ec.ECDSA(hashes.SHA256()))
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
# depending on leading-zero stripping in r and s. We assert both
# extremes still verify, then assert the verifier's hex-length guard
# correctly accepts the actual byte ranges we see in practice.
# --------------------------------------------------------------------------


def _produce_typical_sig(priv: ec.EllipticCurvePrivateKey, body: bytes) -> bytes:
    return priv.sign(body, ec.ECDSA(hashes.SHA256()))


def test_full_length_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A 70-72-byte (full-length r and s) signature verifies."""
    # The signed bytes MUST be exactly the pre-trailer bytes on disk
    # (body terminated by ``\n``), so sign that exact string. Use a
    # different body per attempt so we get different signatures.
    sig = b""
    final_body = b""
    for i in range(200):
        candidate_body = f"x{i}\n".encode("ascii")
        candidate_sig = _produce_typical_sig(priv_a, candidate_body)
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
    """A short signature (≤ 68 bytes — leading zeros stripped) verifies.

    DER stripping makes signature length non-constant; the verifier's
    length guard must not over-tighten.
    """
    sig = b""
    final_body = b""
    for i in range(500):
        candidate_body = f"y{i}\n".encode("ascii")
        candidate_sig = _produce_typical_sig(priv_a, candidate_body)
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
#
# OpenSSL emits several PEM headers for the same underlying key. The
# verifier loads the SubjectPublicKeyInfo form via
# ``serialization.load_pem_public_key``; we should confirm that the
# common shapes a user might paste in all parse correctly.
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


def test_cryptography_generated_pem_loads(tmp_path: Path, priv_a):
    """A PEM produced via ``cryptography``'s ``serialization.PublicFormat.SubjectPublicKeyInfo`` loads."""
    pub_pem = priv_a.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
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
    sig = priv_a.sign(body, ec.ECDSA(hashes.SHA256()))
    target = tmp_path / "rotated.py"
    target.write_bytes(body + TRAILER_PREFIX + sig.hex().encode("ascii") + b"\n")

    key_a_path = tmp_path / "a.pem"
    key_a_path.write_bytes(key_a_pub_pem)
    key_b_path = tmp_path / "b.pem"
    key_b_path.write_bytes(key_b_pub_pem)
    # b first, a second — verifier must try both.
    keys = load_public_keys([str(key_b_path), str(key_a_path)])

    result, _ = verify_file(str(target), keys)
    assert result == VerificationResult.OK


# --------------------------------------------------------------------------
# 7. Deterministic interop: sign with one library, verify with another's parser.
#
# Round-trips:
#   * encode_dss_signature → decode_dss_signature → re-encode → verify
#   * The verifier MUST be robust to any valid DER encoding of (r, s).
# --------------------------------------------------------------------------


def test_manually_encoded_dss_signature_verifies(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A signature constructed from ``encode_dss_signature(r, s)`` verifies.

    Pins that the verifier accepts ANY valid DER (r, s) encoding, not
    just the encoding ``cryptography``'s ``priv.sign`` happens to
    produce. Any third-party DER encoder (KMS, sigstore, custom code)
    will pass this test as long as it's standards-conformant.
    """
    body = b"# DER round-trip\n"
    raw_sig = priv_a.sign(body, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(raw_sig)
    re_encoded = encode_dss_signature(r, s)

    target = tmp_path / "reencoded.py"
    target.write_bytes(body + TRAILER_PREFIX + re_encoded.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, signed = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.OK
    assert signed == body


# --------------------------------------------------------------------------
# 8. Signing-input-byte sensitivity.
#
# Confirm the verifier hashes the EXACT bytes preceding the trailer.
# A signature produced over body + trailing-junk bytes that aren't
# represented on disk must NOT verify; a signature produced over the
# exact disk bytes minus the trailer-with-NL MUST verify.
# --------------------------------------------------------------------------


def test_signing_input_must_match_on_disk_pretrailer_bytes(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """Signature is invalid if signer hashed different bytes than disk."""
    on_disk_body = b"# real body\n"
    # Signer (incorrectly) hashed a different payload.
    fake_signed_payload = b"# different body the signer thought it was signing\n"
    sig = priv_a.sign(fake_signed_payload, ec.ECDSA(hashes.SHA256()))

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
    sig = priv_a.sign(body, ec.ECDSA(hashes.SHA256()))
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
#
# This pins that the verifier accepts ONLY DER. A future refactor that
# "helpfully" accepts both encodings would be a real security regression:
# raw r||s makes signature malleability easier to exploit and removes the
# structural sanity check the DER wrapper provides.
# --------------------------------------------------------------------------


def test_jose_raw_r_s_signature_rejected_as_bad_signature(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A 64-byte raw ``r||s`` signature (the JWS / IEEE P1363 form) is rejected."""
    body = b"def check():\n    return 'ok'\n"
    der_sig = priv_a.sign(body, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der_sig)
    # IEEE P1363 / JWS-style flat encoding: r||s, each padded to 32 bytes.
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
        f"BAD_SIGNATURE; got {result!r}. The verifier accepts ONLY DER. "
        f"A future refactor that adds raw-r||s support is a security "
        f"regression — see the test docstring."
    )


# --------------------------------------------------------------------------
# 10. Legacy PEM shape: ``-----BEGIN EC PUBLIC KEY-----``.
#
# Most OpenSSL versions emit ``-----BEGIN PUBLIC KEY-----`` (SPKI), and
# our docs recipe (``openssl ec -in priv.pem -pubout``) ALWAYS emits
# SPKI. The legacy ``BEGIN EC PUBLIC KEY`` banner wraps raw-EC-point
# bytes, NOT a SubjectPublicKeyInfo structure — they are not byte-
# compatible. ``cryptography.serialization.load_pem_public_key`` rejects
# the mismatch with the standard ``unsupported key format`` error.
#
# This test documents the contract: customers must use SPKI (the openssl
# ``-pubout`` default). A non-SPKI key is rejected loudly, which is the
# right outcome — no silent acceptance of an unintended key shape.
# --------------------------------------------------------------------------


def test_non_spki_pem_rejected_with_clear_error(tmp_path: Path, priv_a):
    """A non-SubjectPublicKeyInfo PEM is rejected with ``unsupported key format``.

    Documents the SPKI requirement and pins the diagnostic so a customer
    who pastes a non-SPKI key gets a clear error.
    """
    from checkov.common.external_checks.verification.errors import (
        SignatureVerificationError,
    )

    spki_pem = priv_a.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    # Rewriting the banner produces a PEM whose body is SPKI but whose
    # banner says "EC PUBLIC KEY" — load_pem_public_key validates the
    # banner-vs-body match and rejects this.
    legacy_pem = (
        spki_pem
        .replace(b"-----BEGIN PUBLIC KEY-----", b"-----BEGIN EC PUBLIC KEY-----")
        .replace(b"-----END PUBLIC KEY-----", b"-----END EC PUBLIC KEY-----")
    )
    pub_path = tmp_path / "wrong_banner.pem"
    pub_path.write_bytes(legacy_pem)

    with pytest.raises(SignatureVerificationError, match="unsupported key format"):
        load_public_keys([str(pub_path)])


# --------------------------------------------------------------------------
# 11. Wrong hash algorithm on the signing side.
#
# The verifier hardcodes SHA-256. If a signer accidentally used SHA-384
# or SHA-512, the signature is structurally valid (DER) but cryptographically
# invalid for the payload-under-SHA-256, so the verifier MUST reject it
# with ``UNKNOWN_KEY`` (not BAD_SIGNATURE — the DER is fine).
#
# This pins the algorithm rigidity: a customer who runs
# ``openssl dgst -sha384 -sign`` will get a clear UNKNOWN_KEY result,
# not a silently-accepted wrong-algorithm signature.
# --------------------------------------------------------------------------


def test_sha384_signed_file_is_rejected(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A signature computed with SHA-384 over the payload is rejected.

    Pins SHA-256 as the only accepted hash. The verifier never tries
    other hashes; the signature simply fails to verify under SHA-256.
    """
    body = b"# wrong-hash signer\n"
    sha384_sig = priv_a.sign(body, ec.ECDSA(hashes.SHA384()))

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
    sha512_sig = priv_a.sign(body, ec.ECDSA(hashes.SHA512()))

    target = tmp_path / "sha512.py"
    target.write_bytes(body + TRAILER_PREFIX + sha512_sig.hex().encode("ascii") + b"\n")

    key_path = tmp_path / "key.pem"
    key_path.write_bytes(key_a_pub_pem)
    result, _ = verify_file(str(target), load_public_keys([str(key_path)]))
    assert result == VerificationResult.UNKNOWN_KEY


# --------------------------------------------------------------------------
# 12. Pre-hashed signing path (operator misconfiguration).
#
# ``openssl pkeyutl -sign`` signs an already-computed digest, not the
# file bytes. If a customer wires their signing pipeline this way by
# mistake, the verifier will see a structurally valid DER signature
# that does not match the file → ``UNKNOWN_KEY``. Pins the diagnostic
# so the customer's support ticket lands with a clear failure code.
# --------------------------------------------------------------------------


def test_pre_hashed_signature_rejected(
    tmp_path: Path, priv_a, key_a_pub_pem: bytes,
):
    """A signature over ``sha256(body)`` (instead of ``body``) is rejected.

    This is the ``openssl pkeyutl -sign`` mistake. The signature is a
    well-formed DER ECDSA pair; it just signs the wrong payload.
    """
    import hashlib
    body = b"# pre-hashed signing mistake\n"
    digest = hashlib.sha256(body).digest()
    # Sign the DIGEST (32 bytes) as if it were the message. The
    # cryptography library will SHA-256 it AGAIN — a classic double-hash
    # bug — and produce a sig that the verifier will reject because the
    # verifier hashes the on-disk body, not the digest of the body.
    sig = priv_a.sign(digest, ec.ECDSA(hashes.SHA256()))

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
