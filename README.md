# QualitySeal

**Local-first quality control, inspection, and non-conformance evidence logger and QuantumGuard sealer for field operators and GCs.**

Offline. Deterministic. Pay once. Compatible with QuantumGuard CONTRACT-v1 and the Operator Pages suite.

## Why QualitySeal?

Field operators, QC inspectors, and general contractors face disputes over quality, material certifications, hold points, and non-conformances. QualitySeal captures the inspection or QC event (results, deficiencies, corrective actions, spec references, media hashes) in the field, then seals it into a client- or auditor-verifiable QuantumGuard evidence bundle.

- No SaaS. No subscription. Runs completely offline after key setup.
- Clients, GCs, owners, or auditors verify the pack with the free QuantumGuard verifier (`qg verify` or HTTP).
- Pairs with SafetySeal for safety, PunchListSeal for deficiencies, CloseSeal for close-out, SubmittalSeal for product data.
- Exports simple CSVs for records.

## Quick Start

```bash
# Optional but recommended for real Ed25519 signatures
pip install cryptography

python3 src/qualityseal.py --demo
python3 src/qualityseal.py --event samples/qc-001.json --out sealed.json
```

Verify the output with the QuantumGuard CLI (from the quantumguard repo):

```bash
qg verify sealed.json
```

Expected verdict: PASS (when using real cryptography).

## What you can sell

| SKU       | Price | Includes                                      |
|-----------|-------|-----------------------------------------------|
| Operator  | $79   | CLI + HTML logger + key setup guide + 1-year email support |
| Command   | $199  | + batch mode + templates + reseller rights for client packs |
| Agency    | $499  | + white-label HTML + design partner onboarding |

Purchase / access: danpennic@gmail.com

Source remains free under Apache-2.0 OR MIT. Commercial Operator Pack sold separately.

## Stack Fit

- Python CLI (same family as SafetySeal, DailySeal, etc.)
- Emits QuantumGuard CONTRACT-v1 bundles (Ed25519, deterministic hashing)
- Local key storage (PEM)
- Ready for integration with the Operator Pages suite

## License

Apache-2.0 OR MIT
