#!/usr/bin/env python3
"""Manual device flow without Android: generate key, enroll, mark attendance.

Examples:
  python scripts/sign_request.py enroll --code ABCD-EF01 --api http://localhost:8000
  python scripts/sign_request.py attendance --uid 04:11:22:33:44:55:66 --pair-id 1 --group-id 1
"""

from __future__ import annotations

import argparse
import base64
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

STATE_PATH = Path(__file__).resolve().parent / ".device_state.json"


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2))


def get_or_create_keys(state: dict) -> tuple[ec.EllipticCurvePrivateKey, str]:
    if "private_key_pem" in state:
        private_key = serialization.load_pem_private_key(
            state["private_key_pem"].encode(), password=None
        )
    else:
        private_key = ec.generate_private_key(ec.SECP256R1())
        state["private_key_pem"] = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_key, public_pem


def sign(private_key: ec.EllipticCurvePrivateKey, payload: bytes) -> str:
    der_sig = private_key.sign(payload, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der_sig)
    raw = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return base64.b64encode(raw).decode()


def signed_request(
    client: httpx.Client,
    private_key: ec.EllipticCurvePrivateKey,
    device_id: str,
    method: str,
    path: str,
    body: dict | None = None,
) -> httpx.Response:
    body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":")) if body is not None else ""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = f"{method.upper()}{path}{body_str}{timestamp}".encode()
    signature = sign(private_key, payload)
    headers = {
        "X-Device-Id": device_id,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Content-Type": "application/json",
    }
    return client.request(method, path, content=body_str if body is not None else None, headers=headers)


def cmd_enroll(args: argparse.Namespace) -> None:
    state = load_state()
    private_key, public_pem = get_or_create_keys(state)
    device_id = state.get("device_id") or f"dev-{uuid.uuid4().hex[:12]}"
    state["device_id"] = device_id
    state["api"] = args.api.rstrip("/")
    save_state(state)

    with httpx.Client(base_url=state["api"], timeout=30.0) as client:
        res = client.post(
            "/v1/enroll",
            json={"code": args.code, "device_id": device_id, "public_key": public_pem},
        )
        print(res.status_code, res.text)
        res.raise_for_status()
        print(f"Enrolled device_id={device_id}")
        print(f"State saved to {STATE_PATH}")


def cmd_attendance(args: argparse.Namespace) -> None:
    state = load_state()
    if "private_key_pem" not in state or "device_id" not in state:
        raise SystemExit("Run enroll first")
    private_key, _ = get_or_create_keys(state)
    api = args.api.rstrip("/") if args.api else state.get("api", "http://localhost:8000")
    body = {
        "uid": args.uid,
        "pair_id": args.pair_id,
        "group_id": args.group_id,
        "event_type": args.event_type,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with httpx.Client(base_url=api, timeout=30.0) as client:
        res = signed_request(
            client, private_key, state["device_id"], "POST", "/v1/attendance", body
        )
        print(res.status_code, res.text)


def cmd_pairs(args: argparse.Namespace) -> None:
    state = load_state()
    private_key, _ = get_or_create_keys(state)
    api = args.api.rstrip("/") if args.api else state.get("api", "http://localhost:8000")
    with httpx.Client(base_url=api, timeout=30.0) as client:
        res = signed_request(client, private_key, state["device_id"], "GET", "/v1/me/pairs")
        print(res.status_code, res.text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate Android reader against API")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_enroll = sub.add_parser("enroll")
    p_enroll.add_argument("--code", required=True)
    p_enroll.add_argument("--api", default="http://localhost:8000")
    p_enroll.set_defaults(func=cmd_enroll)

    p_att = sub.add_parser("attendance")
    p_att.add_argument("--uid", required=True)
    p_att.add_argument("--pair-id", type=int, required=True)
    p_att.add_argument("--group-id", type=int, required=True)
    p_att.add_argument("--event-type", default="check_in", choices=["check_in", "check_out"])
    p_att.add_argument("--api", default=None)
    p_att.set_defaults(func=cmd_attendance)

    p_pairs = sub.add_parser("pairs")
    p_pairs.add_argument("--api", default=None)
    p_pairs.set_defaults(func=cmd_pairs)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
