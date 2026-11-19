#!/usr/bin/env python3
"""
QualitySeal — local-first quality control, inspection, and non-conformance evidence logger.
Compatible with QuantumGuard CONTRACT-v1 and the Operator Pages suite.
Offline after key setup. Deterministic payload hashing.
"""
import argparse
import json
import hashlib
import base64
import os
from datetime import datetime, timezone
from pathlib import Path

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Note: cryptography not installed. Using stub signatures. pip install cryptography for real Ed25519.")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def load_or_create_key(key_path: Path) -> tuple:
    """Returns (private_key_or_None, public_key_hex)"""
    if not CRYPTO_AVAILABLE:
        # Stub for demo
        return None, "00" * 32
    if key_path.exists():
        with open(key_path, "rb") as f:
            priv = serialization.load_pem_private_key(f.read(), password=None)
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return priv, pub_bytes.hex()
    else:
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        pub_bytes = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_path.write_bytes(pem)
        return priv, pub_bytes.hex()

def sign_payload(priv, payload_hash_hex: str) -> str:
    if not CRYPTO_AVAILABLE or priv is None:
        return "00" * 64  # stub
    hash_bytes = bytes.fromhex(payload_hash_hex)
    sig = priv.sign(hash_bytes)
    return sig.hex()

def build_evidence_pack(event: dict, priv, pub_hex: str) -> dict:
    # Deterministic canonical payload
    payload_obj = {
        "version": "1",
        "type": "quality_event",
        "event_id": event.get("event_id", "unknown"),
        "event_type": event.get("event_type", "inspection"),  # inspection, non_conformance, hold_point, material_cert
        "site": event.get("site", ""),
        "client": event.get("client", ""),
        "spec_reference": event.get("spec_reference", ""),
        "notes": event.get("notes", ""),
        "deficiencies": event.get("deficiencies", []),
        "corrective_actions": event.get("corrective_actions", []),
        "status": event.get("status", "accepted"),  # accepted, rejected, conditional, rework
        "media_hashes": event.get("media_hashes", []),
        "logged_at": event.get("logged_at", datetime.now(timezone.utc).isoformat()),
        "operator": event.get("operator", "qc-inspector")
    }
    payload_bytes = json.dumps(payload_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.b64encode(payload_bytes).decode("ascii")
    payload_hash = sha256_hex(payload_bytes)
    signature = sign_payload(priv, payload_hash)

    pack = {
        "version": "1",
        "payload": payload_b64,
        "payload_hash": payload_hash,
        "signature": signature,
        "public_key": pub_hex,
        "alg": "ed25519"
    }
    return pack

def demo():
    sample = {
        "event_id": "QC-2026-042",
        "event_type": "inspection",
        "site": "456 Industrial Blvd, Springfield MO",
        "client": "Acme Construction",
        "spec_reference": "ASTM C39 / Section 03300",
        "notes": "Concrete cylinder break tests complete. All samples meet or exceed specified strength. No deficiencies.",
        "deficiencies": [],
        "corrective_actions": [],
        "status": "accepted",
        "media_hashes": ["sha256-of-test-report.pdf"],
        "operator": "qc-dan"
    }
    key_path = Path.home() / ".qualityseal_key.pem"
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(sample, priv, pub_hex)
    print(json.dumps(pack, indent=2))
    print("\n# Verify with: qg verify <this.json>  (from QuantumGuard)")

def main():
    parser = argparse.ArgumentParser(description="QualitySeal — local quality control evidence logger")
    parser.add_argument("--demo", action="store_true", help="Run demo and print sealed pack")
    parser.add_argument("--event", type=str, help="Path to quality event JSON file")
    parser.add_argument("--out", type=str, help="Output sealed pack path")
    parser.add_argument("--key", type=str, default=str(Path.home() / ".qualityseal_key.pem"), help="Private key path")
    args = parser.parse_args()

    if args.demo:
        demo()
        return

    if not args.event:
        parser.print_help()
        return

    with open(args.event) as f:
        event = json.load(f)

    key_path = Path(args.key)
    priv, pub_hex = load_or_create_key(key_path)
    pack = build_evidence_pack(event, priv, pub_hex)

    out_path = args.out or "sealed_qualityseal.json"
    with open(out_path, "w") as f:
        json.dump(pack, f, indent=2)
    print(f"Sealed pack written to {out_path}")
    print(f"Payload hash: {pack['payload_hash']}")
    print("Verify with QuantumGuard: qg verify", out_path)

if __name__ == "__main__":
    main()
