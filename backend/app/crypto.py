import base64
import hashlib

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature


def normalize_uid(uid: str) -> str:
    cleaned = uid.strip().upper().replace("-", "").replace(" ", "")
    if ":" in cleaned:
        parts = [p for p in cleaned.split(":") if p]
        return ":".join(parts)
    if len(cleaned) % 2 != 0:
        return cleaned
    return ":".join(cleaned[i : i + 2] for i in range(0, len(cleaned), 2))


def build_signed_payload(method: str, path: str, body: str, timestamp: str) -> bytes:
    return f"{method.upper()}{path}{body}{timestamp}".encode("utf-8")


def load_public_key(public_key_pem_or_b64: str) -> ec.EllipticCurvePublicKey:
    raw = public_key_pem_or_b64.strip()
    if "BEGIN" in raw:
        key = serialization.load_pem_public_key(raw.encode("utf-8"))
    else:
        der = base64.b64decode(raw)
        key = serialization.load_der_public_key(der)
    if not isinstance(key, ec.EllipticCurvePublicKey):
        raise ValueError("Public key must be ECDSA")
    return key


def verify_ecdsa_sha256(public_key_material: str, payload: bytes, signature_b64: str) -> bool:
    try:
        public_key = load_public_key(public_key_material)
        signature = base64.b64decode(signature_b64)
        # Accept raw r||s (64 bytes) or DER
        if len(signature) == 64:
            r = int.from_bytes(signature[:32], "big")
            s = int.from_bytes(signature[32:], "big")
            signature = encode_dss_signature(r, s)
        public_key.verify(signature, payload, ec.ECDSA(hashes.SHA256()))
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


def public_key_to_pem(public_key: ec.EllipticCurvePublicKey) -> str:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")


def fingerprint_body(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()
